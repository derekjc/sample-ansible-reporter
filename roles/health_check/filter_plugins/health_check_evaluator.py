#!/bin/python3


class FilterModule(object):
    def filters(self):
        return {"evaluate_health": self.evaluate_health}

    def evaluate_numeric(self, value, thresholds):
        try:
            # Handle different types of input
            if isinstance(value, dict) and "stdout" in value:
                value = value["stdout"]

            # Convert to float and strip any whitespace
            value = float(str(value).strip())

            return {
                "status": (
                    "CRITICAL"
                    if value >= thresholds.get("critical_threshold", 100)
                    else (
                        "WARNING"
                        if value >= thresholds.get("warning_threshold", 80)
                        else "OK"
                    )
                ),
                "value": value,
                "message": f"Current value: {value}%",
            }
        except (ValueError, AttributeError, TypeError) as e:
            return {
                "status": "UNKNOWN",
                "value": value,
                "message": f"Invalid numeric value: {str(e)}",
            }

    def evaluate_service(self, facts, validate):
        service_name = validate.get("name")
        desired_state = validate.get("state", "started")

        services = facts.get("ansible_facts", {}).get("services", {})
        if not services.get(service_name):
            return {
                "status": "CRITICAL",
                "message": f"Service {service_name} not found",
            }

        actual_state = services[service_name].get("state")
        return {
            "status": "OK" if actual_state == desired_state else "CRITICAL",
            "message": f"Service {service_name} is {actual_state}",
        }

    def evaluate_health(self, result, validate, register_name):
        validation_type = validate.get("type", "numeric")

        if validation_type == "numeric":
            return self.evaluate_numeric(result, validate)
        elif validation_type == "service":
            return self.evaluate_service(result, validate)

        return {
            "status": "UNKNOWN",
            "message": f"Unknown validation type: {validation_type}",
        }
