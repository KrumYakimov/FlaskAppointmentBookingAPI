class EmailTemplates:
    SUBJECT_APPOINTMENT_BOOKED = "Your Appointment Has Been Booked"
    SUBJECT_APPOINTMENT_CONFIRMED = "Your Appointment Has Been Confirmed"
    SUBJECT_APPOINTMENT_UPDATED = "Your Appointment Has Been Updated"
    SUBJECT_APPOINTMENT_REJECTED = "Appointment Rejection"
    SUBJECT_APPOINTMENT_CANCELLED = "Appointment Cancellation"

    CONTENT_APPOINTMENT_BOOKED = """
    Dear {first_name},

    Your appointment has been successfully booked!

    Appointment Details:
    - Service: {service_name}
    - Date & Time: {appointment_time}
    - Employee: {employee_name}

    Thank you for choosing us!

    Regards,
    Your Service Team
    """

    CONTENT_APPOINTMENT_CONFIRMED = """
    Dear {first_name},

    We are pleased to inform you that your appointment has been confirmed!

    Appointment Details:
    - Appointment ID: {appointment_id}
    - Service: {service_name}
    - Date & Time: {appointment_time}
    - Staff: {employee_name}

    Thank you for choosing us! If you have any questions or need to make changes to your appointment, please don't hesitate to contact us.

    Best regards,
    Your Service Team
    """

    CONTENT_APPOINTMENT_UPDATED = """
    Dear {first_name},

    We would like to inform you that your appointment has been successfully updated!

    Appointment Details:
    - Appointment ID: {appointment_id}
    - Service: {service_name}
    - New Date & Time: {new_appointment_time}
    - Employee: {employee_name}

    If you have any questions or need to make further changes, please feel free to contact us.

    Thank you for choosing us!

    Best regards,
    Your Service Team
    """

    CONTENT_APPOINTMENT_REJECTED = """
    Dear {first_name},

    We regret to inform you that your appointment with ID {appointment_id} has been rejected.

    If you have any questions or would like to reschedule, please feel free to contact us.

    Thank you for your understanding.

    Best regards,
    Your Service Team
    """

    CONTENT_APPOINTMENT_CANCELLED = """
    Dear {first_name},

    We regret to inform you that your appointment with ID {appointment_id} has been canceled.

    If you have any questions or would like to reschedule, please feel free to contact us.

    Thank you for your understanding.

    Best regards,
    Your Service Team
    """

    CONTENT_REMINDER_1_DAY = """
    Dear {customer_name},

    This is a reminder that you have an appointment scheduled for {appointment_time}.

    Thank you for choosing us!

    Best regards,
    Your Service Team
    """

    CONTENT_REMINDER_2_HOURS = """
    Dear {customer_name},

    This is a reminder that your appointment is coming up at {appointment_time}.

    Thank you for choosing us!

    Best regards,
    Your Service Team
    """
