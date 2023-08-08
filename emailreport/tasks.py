from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime,timedelta
from celery import shared_task
import traceback
import smtplib

@shared_task
def send_daily_reports_task():
    try:
        from emailreport.models import product,User,serials,entity_list,report,startenddates
        users = User.objects.filter(is_created_product=True)
        for user in users:
            try:
                report_type=report.objects.get(user_details=user)
            except report.DoesNotExist:
                print(f"{user.username} hasn't registered for email option.")
                continue
            subject = "Report for your Products"
            report_content = ""
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            if user.is_subscribed == True:
                entities = entity_list.objects.filter(user_details=user)
                for entity in entities:
                    report_content += f"Daily Report for {entity.entity_name}\n"
                    try:
                        products = product.objects.filter(user_details=user,linked_entity=entity)
                        for prod in products:
                            serial_obj=serials.objects.filter(linked_product=prod)
                            if report_type.daily_report == True:
                                start_date = datetime.today().date()
                                end_date = start_date
                                total_serials = serial_obj.filter(created_date__range=(start_date, end_date)).count()
                                serials_commissioned=serial_obj.filter(commissioned_date__range=(start_date, end_date),is_commissioned=True).count()
                                serials_packed=serial_obj.filter(packed_date__range=(start_date, end_date),is_packed=True).count()
                                serials_shipped=serial_obj.filter(shipped_date__range=(start_date, end_date),is_shipped=True).count()
                                serials_decommissioned=total_serials-serials_commissioned
                                report_content += f"Daily Report for {prod.product_name}:\n"
                                report_content += f"Total Serials: {total_serials}\n"
                                report_content += f"Serials Commissioned: {serials_commissioned}\n"
                                report_content += f"Serials Packed: {serials_packed}\n"
                                report_content += f"Serials Shipped: {serials_shipped}\n"
                                report_content += f"Serials Decommissioned: {serials_decommissioned}\n\n"
                            if report_type.weekly_report == True:
                                today = datetime.today().date()
                                start_date = today - timedelta(days=today.weekday())
                                end_date = start_date + timedelta(days=6)
                                total_serials = serial_obj.filter(created_date__range=(start_date, end_date)).count()
                                serials_commissioned=serial_obj.filter(commissioned_date__range=(start_date, end_date),is_commissioned=True).count()
                                serials_packed=serial_obj.filter(packed_date__range=(start_date, end_date),is_packed=True).count()
                                serials_shipped=serial_obj.filter(shipped_date__range=(start_date, end_date),is_shipped=True).count()
                                serials_decommissioned=total_serials-serials_commissioned
                                report_content += f"Daily Report for {prod.product_name}:\n"
                                report_content += f"Total Serials: {total_serials}\n"
                                report_content += f"Serials Commissioned: {serials_commissioned}\n"
                                report_content += f"Serials Packed: {serials_packed}\n"
                                report_content += f"Serials Shipped: {serials_shipped}\n"
                                report_content += f"Serials Decommissioned: {serials_decommissioned}\n\n"
                            if report_type.date_range_report == True:
                                startenddate=startenddates.objects.get(user_details=user)
                                start_date=startenddate.start_date
                                end_date=startenddate.end_date
                                total_serials = serial_obj.filter(created_date__range=(start_date, end_date)).count()
                                serials_commissioned=serial_obj.filter(commissioned_date__range=(start_date, end_date),is_commissioned=True).count()
                                serials_packed=serial_obj.filter(packed_date__range=(start_date, end_date),is_packed=True).count()
                                serials_shipped=serial_obj.filter(shipped_date__range=(start_date, end_date),is_shipped=True).count()
                                serials_decommissioned=total_serials-serials_commissioned
                                report_content += f"Daily Report for {prod.product_name}:\n"
                                report_content += f"Total Serials: {total_serials}\n"
                                report_content += f"Serials Commissioned: {serials_commissioned}\n"
                                report_content += f"Serials Packed: {serials_packed}\n"
                                report_content += f"Serials Shipped: {serials_shipped}\n"
                                report_content += f"Serials Decommissioned: {serials_decommissioned}\n\n"
                    except product.DoesNotExist:
                        print("no product under this entity")
                        continue
                current_date = datetime.today()
                is_sunday = current_date.weekday() == 6
                if report_content and report_type.daily_report == True:
                    message = "Here is the daily report for your products:\n\n" + report_content
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                if report_content and (report_type.weekly_report == True and is_sunday == True):
                    message = "Here is the weekly report for your products:\n\n" + report_content
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)   

        return {
            "statusCode": 200,
            "body": "Daily reports sent successfully."
        }
    except smtplib.SMTPException as smtp_ex:
        return {
            "statusCode": 500,
            "body": f"Error sending daily reports. SMTPException: {smtp_ex}"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": "Error sending daily reports."
        }
