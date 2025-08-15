# Gmail Push Notifications Setup Guide

This guide explains how to set up Gmail push notifications using Google Cloud Pub/Sub to trigger the expense automation workflow instead of polling.

## Overview

Instead of polling Gmail every few minutes, we'll use Gmail's push notification system that sends real-time notifications when new emails arrive. This is more efficient and provides immediate processing.

## Prerequisites

- Google Cloud Project
- Gmail API enabled
- Google Cloud Pub/Sub API enabled
- n8n instance accessible via HTTPS (for webhook)

## Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable billing for the project

### 1.2 Enable Required APIs

Enable these APIs in your Google Cloud project:

```bash
# Enable Gmail API
gcloud services enable gmail.googleapis.com

# Enable Pub/Sub API
gcloud services enable pubsub.googleapis.com

# Enable Cloud Functions API (if using)
gcloud services enable cloudfunctions.googleapis.com
```

Or enable via Google Cloud Console:
- Go to **APIs & Services** → **Library**
- Search and enable:
  - Gmail API
  - Cloud Pub/Sub API
  - Cloud Functions API (optional)

### 1.3 Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `gmail-push-notifications`
4. Description: `Service account for Gmail push notifications`
5. Click **Create and Continue**
6. Grant these roles:
   - **Pub/Sub Publisher**
   - **Pub/Sub Subscriber**
   - **Gmail API** (if needed)
7. Click **Done**

### 1.4 Create and Download Key

1. Click on the created service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create New Key**
4. Choose **JSON** format
5. Download the key file
6. Keep it secure - this contains sensitive credentials

## Step 2: Pub/Sub Topic Setup

### 2.1 Create Pub/Sub Topic

```bash
# Create topic
gcloud pubsub topics create gmail-notifications

# Verify topic created
gcloud pubsub topics list
```

### 2.2 Create Pub/Sub Subscription

```bash
# Create subscription
gcloud pubsub subscriptions create gmail-subscription \
  --topic=gmail-notifications \
  --ack-deadline=60
```

## Step 3: Gmail Watch Setup

### 3.1 Create Gmail Watch Request

You'll need to set up a Gmail watch on your mailbox. This can be done via:

#### Option A: Google Cloud Function (Recommended)

Create a Cloud Function to handle Gmail watch setup:

```javascript
// index.js
const {google} = require('googleapis');
const gmail = google.gmail('v1');

exports.setupGmailWatch = async (req, res) => {
  try {
    // Authenticate with service account
    const auth = new google.auth.GoogleAuth({
      keyFile: 'path/to/service-account-key.json',
      scopes: ['https://www.googleapis.com/auth/gmail.readonly']
    });

    const authClient = await auth.getClient();

    // Set up Gmail watch
    const response = await gmail.users.watch({
      auth: authClient,
      userId: 'me',
      requestBody: {
        topicName: 'projects/YOUR_PROJECT_ID/topics/gmail-notifications',
        labelIds: ['INBOX'],
        labelFilterAction: 'include'
      }
    });

    res.json({
      success: true,
      historyId: response.data.historyId,
      expiration: response.data.expiration
    });
  } catch (error) {
    console.error('Error setting up Gmail watch:', error);
    res.status(500).json({error: error.message});
  }
};
```

#### Option B: Direct API Call

```bash
# Set up Gmail watch via API
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topicName": "projects/YOUR_PROJECT_ID/topics/gmail-notifications",
    "labelIds": ["INBOX"],
    "labelFilterAction": "include"
  }' \
  https://gmail.googleapis.com/gmail/v1/users/me/watch
```

### 3.2 Renew Watch Periodically

Gmail watch expires after 7 days. Set up a cron job to renew it:

```bash
# Cron job to renew watch every 6 days
0 0 */6 * * /path/to/renew-gmail-watch.sh
```

## Step 4: n8n Webhook Configuration

### 4.1 Get n8n Webhook URL

1. In your n8n instance, the workflow creates a webhook at:
   ```
   https://your-n8n-domain.com/webhook/gmail-webhook
   ```

2. Note down this URL for Pub/Sub configuration

### 4.2 Create Push Subscription

```bash
# Create push subscription to n8n webhook
gcloud pubsub subscriptions create n8n-gmail-subscription \
  --topic=gmail-notifications \
  --push-endpoint=https://your-n8n-domain.com/webhook/gmail-webhook \
  --push-auth-service-account=gmail-push-notifications@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 4.3 Configure Authentication

If your n8n webhook requires authentication:

```bash
# Create push subscription with authentication
gcloud pubsub subscriptions create n8n-gmail-subscription \
  --topic=gmail-notifications \
  --push-endpoint=https://your-n8n-domain.com/webhook/gmail-webhook \
  --push-auth-service-account=gmail-push-notifications@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --push-auth-token=YOUR_WEBHOOK_TOKEN
```

## Step 5: Testing the Setup

### 5.1 Test Pub/Sub Message

```bash
# Publish test message to topic
gcloud pubsub topics publish gmail-notifications \
  --message="Test message from Gmail"
```

### 5.2 Test Gmail Notification

1. Send yourself an email
2. Check n8n executions to see if webhook was triggered
3. Verify the email content was fetched and processed

### 5.3 Monitor Pub/Sub

```bash
# Check subscription status
gcloud pubsub subscriptions describe n8n-gmail-subscription

# View recent messages
gcloud pubsub subscriptions pull n8n-gmail-subscription --auto-ack
```

## Step 6: Production Considerations

### 6.1 Security

- Use HTTPS for n8n webhook
- Implement webhook authentication
- Rotate service account keys regularly
- Use least privilege principle for IAM roles

### 6.2 Monitoring

Set up monitoring for:

```bash
# Monitor subscription metrics
gcloud pubsub subscriptions describe n8n-gmail-subscription \
  --format="value(numUndeliveredMessages,numOutstandingMessages)"

# Set up alerts for failed deliveries
gcloud pubsub subscriptions update n8n-gmail-subscription \
  --dead-letter-topic=dead-letter-topic
```

### 6.3 Error Handling

Create a dead letter topic for failed messages:

```bash
# Create dead letter topic
gcloud pubsub topics create dead-letter-topic

# Update subscription with dead letter policy
gcloud pubsub subscriptions update n8n-gmail-subscription \
  --dead-letter-topic=dead-letter-topic \
  --max-delivery-attempts=5
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving messages**
   - Check n8n webhook URL is accessible
   - Verify Pub/Sub subscription is active
   - Check authentication settings

2. **Gmail watch expired**
   - Set up automatic renewal
   - Check service account permissions

3. **Permission errors**
   - Verify service account has required roles
   - Check Gmail API quota limits

### Debug Commands

```bash
# Check Gmail watch status
gcloud pubsub topics list-subscriptions gmail-notifications

# View webhook logs
gcloud pubsub subscriptions pull n8n-gmail-subscription --limit=10

# Test webhook endpoint
curl -X POST https://your-n8n-domain.com/webhook/gmail-webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

## Benefits of Push vs Polling

### Push Notifications (Current Setup)
- ✅ Real-time processing
- ✅ Lower latency
- ✅ Reduced API calls
- ✅ Better resource utilization
- ✅ Immediate response to new emails

### Polling (Previous Setup)
- ❌ Delayed processing
- ❌ Higher API usage
- ❌ Resource waste
- ❌ Potential rate limiting

## Cost Optimization

- Monitor Pub/Sub usage
- Set up billing alerts
- Use appropriate message retention
- Clean up old subscriptions

This setup provides a robust, scalable solution for real-time Gmail processing with your expense automation workflow.
