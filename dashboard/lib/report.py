from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_maintenance_report(
    machine_name,
    health,
    prediction,
    tasks
):

    buffer = BytesIO()


    doc = SimpleDocTemplate(
        buffer
    )


    styles = getSampleStyleSheet()

    story = []


    story.append(
        Paragraph(
            f"Predictive Maintenance Report - {machine_name}",
            styles["Title"]
        )
    )


    story.append(
        Spacer(1, 12)
    )


    # Health Summary

    story.append(
        Paragraph(
            f"""
            <b>Machine:</b> {machine_name}<br/>
            <b>Status:</b> {health.get('status','Unknown')}<br/>
            <b>Risk Score:</b> {prediction.get('probability',0)*100:.1f}%<br/>
            """,
            styles["BodyText"]
        )
    )


    story.append(
        Spacer(1, 12)
    )


    # AI Diagnosis

    story.append(
        Paragraph(
            "AI Diagnostic Factors",
            styles["Heading2"]
        )
    )


    for factor in prediction.get(
        "top_factors",
        []
    ):

        story.append(
            Paragraph(
                f"""
                {factor['feature']}
                Impact:
                {factor['impact']*100:.1f}%
                """,
                styles["BodyText"]
            )
        )


    story.append(
        Spacer(1, 12)
    )


    # Maintenance History

    story.append(
        Paragraph(
            "Maintenance History",
            styles["Heading2"]
        )
    )


    if tasks:

        for task in tasks:

            story.append(
                Paragraph(
                    f"""
                    Work Order:
                    {task['description']}<br/>

                    Status:
                    {task['status']}<br/>

                    Technician:
                    {task.get('technician','Unassigned')}
                    """,
                    styles["BodyText"]
                )
            )

            story.append(
                Spacer(1,8)
            )

    else:

        story.append(
            Paragraph(
                "No maintenance history recorded.",
                styles["BodyText"]
            )
        )


    doc.build(
        story
    )


    buffer.seek(0)


    return buffer
