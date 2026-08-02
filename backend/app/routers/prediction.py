import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.prediction import PredictionResponse

from app.services.alert_service import generate_alert
from app.services.notifications import send_alert_email
from app.services.risk_service import calculate_risk_level, get_latest_prediction
from app.services.sensor_validation import out_of_range_fields, violation_messages
from app.services.tenancy import get_owned_machine_or_404

from app.ml import model_loader
from app.ml.predict import predict_failure
from app.ml.explain import get_feature_importance

from pydantic import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


class PredictionRequest(BaseModel):

    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float



@router.post("/")
def predict(
    request: PredictionRequest,
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    machine = get_owned_machine_or_404(db, machine_id, current_user.account_id)

    violations = out_of_range_fields(
        air_temperature=request.air_temperature,
        process_temperature=request.process_temperature,
        rotational_speed=request.rotational_speed,
        torque=request.torque,
        tool_wear=request.tool_wear,
    )

    if violations:
        raise HTTPException(
            status_code=422,
            detail=violation_messages(violations),
        )

    result = predict_failure(
        air_temperature=request.air_temperature,
        process_temperature=request.process_temperature,
        rotational_speed=request.rotational_speed,
        torque=request.torque,
        tool_wear=request.tool_wear
    )


    # Save prediction

    prediction_record = Prediction(
        machine_id=machine_id,
        prediction=result["prediction"],
        probability=result["probability"],
        top_factors=result["top_factors"],
        input_features={
            "air_temperature": request.air_temperature,
            "process_temperature": request.process_temperature,
            "rotational_speed": request.rotational_speed,
            "torque": request.torque,
            "tool_wear": request.tool_wear,
        },
        model_version=model_loader.MODEL_VERSION,
    )


    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

    # Computed once, up front, via the single canonical classifier (see
    # app.services.risk_service.calculate_risk_level) - used both in the
    # response below and in the work-order logic further down, so nothing
    # else in this endpoint re-derives its own risk tier from probability.
    risk_level = calculate_risk_level(prediction_record.probability)

    logger.info(
        "Prediction created id=%s machine_id=%s probability=%s",
        prediction_record.id,
        machine_id,
        prediction_record.probability,
    )



    # Generate alert

    alert_data = generate_alert(
        prediction_record
    )


    created_alert = None


    if alert_data:


        created_alert = Alert(
            machine_id=machine_id,
            probability=prediction_record.probability,
            severity=alert_data["severity"],
            message=alert_data["message"],
            recommended_action=alert_data["recommended_action"]
        )


        db.add(created_alert)
        db.commit()
        db.refresh(created_alert)

        logger.info(
            "Alert created id=%s machine_id=%s severity=%s",
            created_alert.id,
            machine_id,
            created_alert.severity,
        )

        send_alert_email(created_alert, machine)



        # -----------------------------
        # AUTOMATIC WORK ORDER CREATION
        # -----------------------------

        if risk_level == "CRITICAL":

            description = (
                "URGENT: Immediate inspection required. "
                "Critical failure risk detected."
            )


        elif risk_level == "WARNING":

            description = (
                "Preventive maintenance required. "
                "Elevated failure risk detected."
            )


        else:

            description = None



        if description:


            maintenance_task = MaintenanceTask(
                machine_id=machine_id,
                alert_id=created_alert.id,
                description=description,
                technician="Unassigned",
                status="OPEN"
            )


            db.add(maintenance_task)
            db.commit()

            logger.info(
                "Maintenance task auto-created machine_id=%s alert_id=%s",
                machine_id,
                created_alert.id,
            )



    return {

        "machine_id": machine_id,

        "prediction": result["prediction"],

        "probability": result["probability"],

        "risk_level": risk_level,

        "top_factors": result["top_factors"],

        "model_version": prediction_record.model_version,

        "alert_created": bool(created_alert),

        "created_at": prediction_record.created_at

    }




@router.get("/machines/{machine_id}")
def predict_latest(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the most recently stored prediction for this machine -
    performs no inference and creates no new Prediction row (a GET must be
    read-only). Predictions are created by the write paths that actually
    produce new sensor data: POST /prediction/, POST /sensor_readings/, and
    POST /sensor_readings/bulk.
    """

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    prediction = get_latest_prediction(db, machine_id)

    if prediction is None:
        return {
            "error": "No prediction available yet for this machine."
        }

    return {
        "machine_id": machine_id,
        "sensor_reading_id": prediction.sensor_reading_id,
        "prediction_id": prediction.id,
        "prediction": prediction.prediction,
        "probability": prediction.probability,
        "risk_level": calculate_risk_level(prediction.probability),
        "top_factors": prediction.top_factors,
        "input_features": prediction.input_features,
        "model_version": prediction.model_version,
    }



@router.get("/history/{machine_id}", response_model=list[PredictionResponse])
def prediction_history(
    machine_id: int,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    predictions = (

        db.query(Prediction)

        .filter(
            Prediction.machine_id == machine_id
        )

        .order_by(
            Prediction.created_at.asc()
        )

        .offset(offset)

        .limit(limit)

        .all()

    )


    return predictions



@router.get("/explanation")
def explanation():

    return {

        "feature_importance":
            get_feature_importance(),

        "model_info": {
            "version": model_loader.MODEL_VERSION,
            "algorithm": model_loader.metadata.get("algorithm"),
            "trained_at": model_loader.metadata.get("trained_at"),
            "metrics": model_loader.metadata.get("metrics"),
        },

    }
