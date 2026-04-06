#!/bin/bash
# Initialize LocalStack resources for development

echo "Creating SQS queues..."
awslocal sqs create-queue --queue-name neuraprop-inbound
awslocal sqs create-queue --queue-name neuraprop-outbound

echo "Creating S3 bucket..."
awslocal s3 mb s3://neuraprop-storage

echo "LocalStack initialization complete!"
