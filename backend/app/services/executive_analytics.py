def calculate_maintenance_compliance(
    completed: int,
    total: int
):
    if total == 0:
        return 100

    return round((completed / total) * 100)


def calculate_fleet_health_score(
    machine_health_scores: list[float]
):
    if not machine_health_scores:
        return 100

    return round(
        sum(machine_health_scores)
        / len(machine_health_scores),
        1
    )