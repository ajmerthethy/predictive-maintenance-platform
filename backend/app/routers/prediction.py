import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionResponse

from app.services.alert_service import generate_alert
from app.services.risk_service import calculate_risk_level

from app.ml.predict import predict_failure
from app.ml.live_prediction import predict_failure_from_reading
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
    db: Session = Depends(get_db)
):

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
        probability=result["probability"]
    )


    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

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



        # -----------------------------
        # AUTOMATIC WORK ORDER CREATION
        # -----------------------------

        probability = prediction_record.probability
        risk_level = calculate_risk_level(probability)

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

        "top_factors": result["top_factors"],

        "alert_created": bool(created_alert),

        "created_at": prediction_record.created_at

    }




@router.get("/machines/{machine_id}")
def predict_latest(
    machine_id: int,
    db: Session = Depends(get_db)
):

    return predict_failure_from_reading(
        db,
        machine_id
    )



@router.get("/history/{machine_id}", response_model=list[PredictionResponse])
def prediction_history(
    machine_id: int,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

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
            get_feature_importance()

    }
