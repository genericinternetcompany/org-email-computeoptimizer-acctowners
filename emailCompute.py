
import os.path
import boto3
import email
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


s3 = boto3.client("s3")

def lambda_handler(event, context):
    
    #list all the accounts
    client_org = boto3.client('organizations')
    response_org = client.list_accounts(
    NextToken='string',
    MaxResults=123
    )

    #acc_email  = ['Accounts']['Email']

    email_list = []

    for item in response_org['Accounts']:
        email_list += [item['Email']]
        print(item['Email'])

        # pull the files we need from the S3 bucket into the email.
        # Get the records for the triggered event
        FILEOBJ = event["Records"][0]
        
        BUCKET_NAME = str(FILEOBJ['s3']['bucket']['name'])

        KEY = str(FILEOBJ['s3']['object']['key'])

        s3_dir_path = os.path.dirname(KEY)

        account_folder = os.path.basename(s3_dir_path)

        #check if recommendation is for the account owner(id)
        if account_folder == item['Id']:

            SENDER = "ddaksh@amazon.com"

            #RECIPIENT = "ddaksh+org1@amazon.com"
            RECIPIENT = item['Email']

            AWS_REGION = "us-east-1"
            SUBJECT = "Test : EC2 Optimization Recommendation with Attachment"

            # extract the file name from the file.
            FILE_NAME = os.path.basename(KEY) 

            # Using the file name, create a new file location for the lambda.
            TMP_FILE_NAME = '/tmp/' +FILE_NAME

            # Download the file/s from the event (extracted above) to the tmp location
            s3.download_file(BUCKET_NAME, KEY, TMP_FILE_NAME)

            ATTACHMENT = TMP_FILE_NAME

            # The email body for recipients with non-HTML email clients.
            BODY_TEXT = "Hello,\r\nPlease see the attached file related to recent EC2 usage for your account."

            # The HTML body of the email.
            BODY_HTML = """\
            <html>
            <head></head>
            <body>
            <h1>Hello!</h1>
            <p>Please see the attached file related to recent EC2 usage for your account.</p>
            </body>
            </html>
            """

            # The character encoding for the email.
            CHARSET = "utf-8"

            # New SES resource
            client = boto3.client('ses',region_name=AWS_REGION)

            # Create a multipart/mixed parent container.
            msg = MIMEMultipart('mixed')

            msg['Subject'] = SUBJECT 
            msg['From'] = SENDER 
            msg['To'] = RECIPIENT

            # Create a multipart/alternative child container.
            msg_body = MIMEMultipart('alternative')

            # Encode the text and HTML content and set the character encoding
            textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
            htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

            # Add the text and HTML parts to the child container.
            msg_body.attach(textpart)
            msg_body.attach(htmlpart)

            # Define the attachment part and encode it using MIMEApplication.
            att = MIMEApplication(open(ATTACHMENT, 'rb').read())

            # Add a header to tell the email client to treat this part as an attachment,
            
            att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))

            msg.attach(msg_body)

            # Add the attachment to the parent container.
            msg.attach(att)
            print(msg)
            try:

                response = client.send_raw_email(
                    Source=SENDER,
                    Destinations=[
                        RECIPIENT
                    ],
                    RawMessage={
                        'Data':msg.as_string(),
                    },
            #        ConfigurationSetName=CONFIGURATION_SET
                )
            # Display an error if something goes wrong. 
            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                print("Email sent! Message ID:"),
                print(response['MessageId'])



        
