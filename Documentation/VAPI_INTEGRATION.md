# VAPI Integration Guide

This guide explains how to integrate VAPI (Voice AI Platform) with the AI Medical Dispatch System.

## Overview

VAPI is a voice AI platform that allows you to build AI assistants that can make and receive phone calls. This integration allows VAPI to:

1. Receive incoming emergency calls
2. Collect patient information through voice conversation (using OpenAI)
3. Automatically create cases and dispatch ambulances
4. Handle call status updates and transcripts

**Note**: VAPI uses OpenAI for voice conversations. Your local LLM is used for triage analysis when cases are created.

## Prerequisites

1. VAPI account and API key
2. VAPI phone number configured in your dashboard
3. Public URL for webhooks (use ngrok or similar for local development)

## Environment Variables

Add these to your `.env` file in the `backend` directory:

```env
VAPI_API_KEY=your_vapi_api_key_here
VAPI_PHONE_NUMBER_ID=your_phone_number_id_here
```

## VAPI Dashboard Setup

### 1. Configure Assistant Model (Use VAPI's Default OpenAI)

**Important**: Use VAPI's default OpenAI provider for voice conversations. Your local LLM will still be used for triage analysis after the call.

1. In VAPI Dashboard, go to **Assistants** → Select/Create your Assistant
2. In the **Model** or **LLM** section:
   - **Provider**: Select **"OpenAI"** (VAPI's default)
   - **Model**: Choose any OpenAI model (e.g., `gpt-3.5-turbo`, `gpt-4`, etc.)
   - **API Key**: Your OpenAI API key (configured in VAPI dashboard)
   - **Temperature**: `0.7` (recommended for conversational AI)

**Note**: 
- VAPI will use OpenAI for the voice conversation
- Your local LLM will still be used for triage analysis when the case is created
- The `/triage/` endpoint uses your local LLM at `http://localhost:1234`

### 2. Create Function Tool

In VAPI Dashboard, create a function tool:

1. Go to **Tools** section (or **Functions** in Assistant settings)
2. Click **Create Tool** or **Add Function**
3. Select **Function** tool type
4. Configure:
   - **Name**: `create_emergency_case`
   - **Description**: "Create an emergency medical case with patient information"
   - **Server URL**: `https://your-ngrok-url.ngrok.io/vapi/function-call`
     - **Note**: You can also use `/vapi/tool-calls` - both endpoints work (use whichever matches your VAPI version)
   - **Parameters**: Add the following JSON schema:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Patient's full name"
    },
    "age": {
      "type": "integer",
      "description": "Patient's age in years"
    },
    "gender": {
      "type": "string",
      "enum": ["Male", "Female", "Other"],
      "description": "Patient's gender"
    },
    "phone": {
      "type": "string",
      "description": "Patient's phone number"
    },
    "symptoms": {
      "type": "string",
      "description": "Description of patient's symptoms and medical condition"
    },
    "location": {
      "type": "string",
      "description": "Patient's address or location (e.g., '123 Main Street, New York, NY' or 'Central Park, Manhattan'). This will be geocoded to get coordinates for ambulance dispatch."
    }
  },
  "required": ["name", "age", "gender", "symptoms"]
}
```

5. **Save** the tool

### 3. Assign Tool to Assistant

1. Go to **Assistants** → Select your assistant
2. In **Tools** or **Functions** section, add the `create_emergency_case` tool you just created
3. Save the assistant

### 4. Webhooks (Not Required)

**Good news**: If you don't see webhook options, VAPI handles them automatically!

- The **Function Call Webhook** is automatically configured via the tool's **Server URL** (step 2)
- Other webhooks (Status, Server, End Call) are optional and handled by VAPI if needed
- Your backend endpoints are ready to receive webhook calls automatically

**Important**: Make sure your local LLM server is running on `http://localhost:1234` before making calls.

### 5. Configure System Prompt

In your VAPI Assistant settings, add this system prompt:

```
You are an AI medical emergency assistant for voice calls. Your primary goal is to collect a patient's details (name, age, gender, phone, symptoms) to dispatch medical help.

Your Conversational Flow:
1. Start by greeting the caller and asking about their medical emergency
2. Ask one or two clarifying questions about the symptoms to assess the situation
3. Collect the patient's details: name, age, gender, and phone number
4. Once you have all the information, call the function create_emergency_case with the collected data

Communication Style:
- Speak naturally and professionally
- Be empathetic and reassuring
- Ask questions clearly and wait for responses
- Confirm information when needed

Important:
- Always call the create_emergency_case function when you have collected all required information
- Make sure to get accurate information before creating the case
```

## API Endpoints

### Custom Model Provider (Optional - Not Required)
- **URL**: `POST /vapi/model`
- **Purpose**: Optional endpoint if you want to use your local LLM for conversations
- **Note**: By default, VAPI uses OpenAI for conversations. Your local LLM is used for triage analysis.

### Status Webhook
- **URL**: `POST /vapi/status`
- **Purpose**: Receives call status updates from VAPI
- **Handles**: Call start, progress, and end events

### Function Call Webhook
- **URL**: `POST /vapi/function-call`
- **Purpose**: Executes functions requested by VAPI assistant
- **Handles**: `create_emergency_case` function calls

### Server Webhook
- **URL**: `POST /vapi/server`
- **Purpose**: Receives real-time message updates during calls
- **Handles**: Transcript updates and conversation state

### End Call Webhook
- **URL**: `POST /vapi/end-call`
- **Purpose**: Final cleanup when call ends
- **Handles**: Session cleanup and data processing

### Configuration Endpoint
- **URL**: `GET /vapi/config`
- **Purpose**: Check VAPI configuration status
- **Returns**: Configuration status and webhook endpoints

### Initiate Call Endpoint
- **URL**: `POST /vapi/initiate-call?phone_number=+1234567890`
- **Purpose**: Make outbound calls via VAPI
- **Parameters**: 
  - `phone_number`: Phone number to call (E.164 format)
  - `assistant_id`: (Optional) VAPI assistant ID

### Active Calls Endpoint
- **URL**: `GET /vapi/calls`
- **Purpose**: View active call sessions (debugging)
- **Returns**: List of active call sessions

## Workflow

### Incoming Call Flow (Step-by-Step)

1. **Call Received**: Patient calls your VAPI phone number
2. **Status Update**: VAPI sends status webhook to `/vapi/status` (status: "ringing" or "started")
3. **Conversation**: VAPI assistant greets caller and collects:
   - Patient's name
   - Age
   - Gender
   - Phone number
   - Symptoms/medical condition
   - Location/address (important for ambulance dispatch)
4. **Function Call (DURING CALL)**: When AI has collected all information, it automatically calls `create_emergency_case` function
   - This triggers `/vapi/function-call` webhook
   - Backend creates case via `/triage/` endpoint
   - Case is **saved to database immediately**
   - Patient hears: "Emergency case created successfully. Help is on the way."
5. **Ambulance Dispatch**: System automatically:
   - Analyzes symptoms with AI triage
   - Selects best ambulance based on location, ETA, and fuel
   - Dispatches ambulance
6. **Call End**: Patient hangs up
   - VAPI sends end call webhook to `/vapi/status` (status: "ended")
   - If case was already created, no duplicate case is created
   - Session is logged and cleaned up

**Important**: The case is created **DURING the call**, not after hanging up. The patient should hear confirmation that help is on the way before ending the call.

### Outbound Call Flow

1. **Initiate Call**: Call `/vapi/initiate-call` with phone number
2. **VAPI Handles**: VAPI makes the call and manages conversation
3. **Follows Same**: Follows the same workflow as incoming calls

## Testing

### Test Configuration
```bash
curl http://localhost:8000/vapi/config
```

### Test Function Call
You can test the function call endpoint directly:

```bash
curl -X POST http://localhost:8000/vapi/function-call \
  -H "Content-Type: application/json" \
  -d '{
    "functionCall": {
      "name": "create_emergency_case",
      "parameters": {
        "name": "John Doe",
        "age": 35,
        "gender": "Male",
        "phone": "+1234567890",
        "symptoms": "Chest pain and shortness of breath"
      }
    },
    "call": {
      "id": "test-call-123",
      "from": "+1234567890"
    }
  }'
```

### View Active Sessions
```bash
curl http://localhost:8000/vapi/calls
```

## Troubleshooting

### Webhooks Not Receiving
1. Check ngrok is running and URL is correct
2. Verify webhook URLs in VAPI dashboard
3. Check server logs for incoming requests
4. Ensure firewall allows incoming connections

### Function Calls Not Working
1. Verify function is configured in VAPI dashboard
2. Check function name matches exactly: `create_emergency_case`
3. Verify required parameters are provided
4. Check backend logs for errors

### Cases Not Creating
1. Verify triage endpoint is accessible: `POST /triage/`
2. Check patient data format
3. Verify database connection
4. Check logs for triage errors

## Security Considerations

1. **API Key Security**: Never commit API keys to version control
2. **Webhook Verification**: Consider implementing webhook signature verification
3. **HTTPS**: Always use HTTPS for webhook URLs in production
4. **Rate Limiting**: Implement rate limiting on webhook endpoints
5. **Data Privacy**: Ensure patient data is handled according to regulations

## Next Steps

1. Configure VAPI assistant in dashboard
2. Set up webhook URLs
3. Test with a phone call
4. Monitor logs for any issues
5. Adjust assistant prompts based on real conversations

