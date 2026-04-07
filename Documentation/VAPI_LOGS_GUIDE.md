# VAPI Backend Logs Guide

This guide shows you **exactly what logs you should see** in your backend console when a VAPI call is working correctly.

## 🔍 Quick Checklist

If you see these logs, everything is working:
- ✅ `🌐 INCOMING REQUEST` - Request reached your server
- ✅ `🔔 VAPI STATUS WEBHOOK RECEIVED` - Call started
- ✅ `🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED` - Case creation triggered
- ✅ `✅ Case Data Received` - Case created successfully
- ✅ `✅ Emergency case created via VAPI function call` - Case saved to database

---

## 📋 Complete Log Sequence (Normal Flow)

### 1. Call Starts - Status Webhook

```
================================================================================
🌐 INCOMING REQUEST: POST /vapi/status
   Query params: {}
   Client: xxx.xxx.xxx.xxx
   Headers: {...}
================================================================================
================================================================================
🔔 VAPI STATUS WEBHOOK RECEIVED
📍 URL: http://localhost:8000/vapi/status
📍 Method: POST
📍 Headers: {...}
================================================================================
📥 VAPI Status Update Body: {
  "call": {
    "id": "call-abc123",
    "status": "started",
    "from": "+1234567890",
    "to": "+0987654321"
  }
}
✅ VAPI Status webhook processed successfully
✅ Response: 200 - 0.025s
```

### 2. Conversation Messages (Server Webhook)

```
================================================================================
🌐 INCOMING REQUEST: POST /vapi/server
   Query params: {}
   Client: xxx.xxx.xxx.xxx
   Headers: {...}
================================================================================
================================================================================
🔔 VAPI SERVER WEBHOOK RECEIVED
📍 URL: http://localhost:8000/vapi/server
📍 Method: POST
📍 Headers: {...}
================================================================================
📥 VAPI Server Request Body: {
  "message": {
    "role": "user",
    "content": "I have chest pain"
  },
  "call": {
    "id": "call-abc123"
  }
}
💬 Message Data: {...}
📞 Call Data: {...}
🆔 Call ID: call-abc123
💬 User message stored: I have chest pain
✅ Response: 200 - 0.015s
```

### 3. Function Call - Case Creation (CRITICAL)

```
================================================================================
🌐 INCOMING REQUEST: POST /vapi/function-call
   Query params: {}
   Client: xxx.xxx.xxx.xxx
   Headers: {...}
================================================================================
================================================================================
🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED
📍 URL: http://localhost:8000/vapi/function-call
📍 Method: POST
📍 Headers: {...}
================================================================================
📥 VAPI Function Call Body: {
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
    "id": "call-abc123",
    "from": "+1234567890"
  }
}
📞 Function: create_emergency_case, Parameters: {...}
📞 Call ID: call-abc123, From: +1234567890
📋 Triage Payload: {
  "name": "John Doe",
  "age": 35,
  "gender": "Male",
  "contact": "+1234567890",
  "symptoms": "Chest pain and shortness of breath",
  "location": "Location from voice call",
  "latitude": null,
  "longitude": null
}
📡 Triage Response Status: 200
📡 Triage Response Headers: {...}
✅ Case Data Received: {
  "id": 123,
  "triage_level": "Emergency",
  "symptoms": "Chest pain, shortness of breath",
  "status": "pending",
  "patient_name": "John Doe"
}
💾 Session updated for call call-abc123 - Case ID: 123
✅ Case 123 successfully created and stored in database
✅ Emergency case created via VAPI function call: Case ID 123
📤 Returning result: {
  "success": true,
  "message": "Emergency case created successfully. Help is on the way.",
  "case_id": 123
}
✅ Response: 200 - 1.234s
```

### 4. Call Ends - Status Webhook

```
================================================================================
🌐 INCOMING REQUEST: POST /vapi/status
   Query params: {}
   Client: xxx.xxx.xxx.xxx
   Headers: {...}
================================================================================
================================================================================
🔔 VAPI STATUS WEBHOOK RECEIVED
📍 URL: http://localhost:8000/vapi/status
📍 Method: POST
📍 Headers: {...}
================================================================================
📥 VAPI Status Update Body: {
  "call": {
    "id": "call-abc123",
    "status": "ended",
    "from": "+1234567890",
    "to": "+0987654321"
  }
}
✅ Call call-abc123 ended. Case 123 was already created during the call.
📋 Call call-abc123 session summary: {
  "call_id": "call-abc123",
  "from": "+1234567890",
  "to": "+0987654321",
  "status": "ended",
  "transcript": [...],
  "patient_data": {...},
  "case_id": 123
}
✅ VAPI Status webhook processed successfully
✅ Response: 200 - 0.032s
```

---

## ⚠️ What to Look For (Troubleshooting)

### ✅ Good Signs (Everything Working)

1. **Request Reaching Server**
   - You see `🌐 INCOMING REQUEST` logs
   - Status code is `200`

2. **Status Webhooks Working**
   - You see `🔔 VAPI STATUS WEBHOOK RECEIVED`
   - Call status changes: `started` → `ended`

3. **Function Call Working** ⭐ MOST IMPORTANT
   - You see `🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED`
   - Function name is `create_emergency_case`
   - You see `✅ Case Data Received` with a case ID
   - You see `✅ Emergency case created via VAPI function call`

4. **Case Saved to Database**
   - Case ID appears in logs
   - No duplicate case creation on call end

### ❌ Warning Signs (Issues)

1. **No Logs At All**
   - ❌ VAPI not reaching your server
   - **Fix**: Check ngrok URL, webhook URLs in VAPI dashboard

2. **Status Webhooks but No Function Call**
   - ❌ AI not calling the function
   - **Fix**: Check system prompt, function tool configuration

3. **Function Call but No Case Created**
   - ❌ Error in case creation
   - **Look for**: `❌ Triage endpoint error` or validation errors
   - **Fix**: Check database connection, triage endpoint

4. **JSON Parsing Errors**
   - ❌ `❌ Could not parse as JSON`
   - **Fix**: Check VAPI webhook format

5. **Timeout Errors**
   - ❌ `❌ Timeout waiting for triage endpoint`
   - **Fix**: Check local LLM server, increase timeout

---

## 🔍 Quick Debug Commands

### Check if server is receiving requests
```bash
# Start your backend and watch for logs
# Any request should show: 🌐 INCOMING REQUEST
```

### Test function call endpoint manually
```bash
curl -X POST http://localhost:8000/vapi/function-call \
  -H "Content-Type: application/json" \
  -d '{
    "functionCall": {
      "name": "create_emergency_case",
      "parameters": {
        "name": "Test Patient",
        "age": 30,
        "gender": "Male",
        "phone": "+1234567890",
        "symptoms": "Test symptoms"
      }
    },
    "call": {
      "id": "test-call-123",
      "from": "+1234567890"
    }
  }'
```

### Check recent calls
```bash
curl http://localhost:8000/vapi/debug/recent-calls
```

### Check VAPI configuration
```bash
curl http://localhost:8000/vapi/config
```

---

## 📊 Expected Log Frequency

During a **normal call** (5-10 minutes), you should see:

- **1-2** Status webhooks (start + end)
- **1** Function call webhook (when case is created)
- **10-50** Server webhooks (conversation messages)
- **Total**: ~15-55 log entries per call

---

## 🎯 Key Log Messages to Watch

| Log Message | Meaning | Action |
|------------|---------|--------|
| `🔔 VAPI STATUS WEBHOOK RECEIVED` | Call status update | Normal |
| `🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED` | Case creation triggered | ⭐ Critical |
| `✅ Case Data Received` | Case created successfully | ✅ Success |
| `✅ Emergency case created via VAPI function call` | Case saved to DB | ✅ Success |
| `❌ Could not parse as JSON` | Webhook format issue | ❌ Fix needed |
| `❌ Triage endpoint error` | Case creation failed | ❌ Fix needed |
| `⚠️ No case was created during the call` | Function not called | ⚠️ Check AI prompt |

---

## 💡 Pro Tips

1. **Filter Logs**: Use `grep` to filter logs:
   ```bash
   # Watch only function calls
   tail -f backend.log | grep "FUNCTION CALL"
   
   # Watch only errors
   tail -f backend.log | grep "❌"
   
   # Watch only successful cases
   tail -f backend.log | grep "✅ Emergency case created"
   ```

2. **Check Logs in Real-Time**: Keep your backend console open while testing calls

3. **Compare Logs**: If a call fails, compare the logs with a successful call to find differences

4. **Case ID**: Every successful case creation should show a **Case ID** - verify this appears in your database

---

## 🚨 Emergency Checklist

If **nothing is working**, check in this order:

1. ✅ Backend server is running (`uvicorn` or similar)
2. ✅ ngrok is running and URL is correct
3. ✅ VAPI dashboard webhook URLs use ngrok URL
4. ✅ You see `🌐 INCOMING REQUEST` logs (requests reaching server)
5. ✅ Function tool is configured in VAPI dashboard
6. ✅ System prompt tells AI to call the function
7. ✅ Database is connected and working

---

## 📝 Example: Complete Successful Call Logs

```
2024-01-15 10:30:15 - 🌐 INCOMING REQUEST: POST /vapi/status
2024-01-15 10:30:15 - 🔔 VAPI STATUS WEBHOOK RECEIVED
2024-01-15 10:30:15 - 📥 VAPI Status Update Body: {"call": {"status": "started"}}
2024-01-15 10:30:15 - ✅ Response: 200 - 0.025s

2024-01-15 10:30:20 - 🌐 INCOMING REQUEST: POST /vapi/server
2024-01-15 10:30:20 - 🔔 VAPI SERVER WEBHOOK RECEIVED
2024-01-15 10:30:20 - 💬 User message stored: I have chest pain

2024-01-15 10:32:45 - 🌐 INCOMING REQUEST: POST /vapi/function-call
2024-01-15 10:32:45 - 🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED
2024-01-15 10:32:45 - 📞 Function: create_emergency_case
2024-01-15 10:32:46 - ✅ Case Data Received: {"id": 123, ...}
2024-01-15 10:32:46 - ✅ Emergency case created via VAPI function call: Case ID 123
2024-01-15 10:32:46 - ✅ Response: 200 - 1.234s

2024-01-15 10:35:00 - 🌐 INCOMING REQUEST: POST /vapi/status
2024-01-15 10:35:00 - 🔔 VAPI STATUS WEBHOOK RECEIVED
2024-01-15 10:35:00 - ✅ Call call-abc123 ended. Case 123 was already created during the call.
```

If you see this pattern, **everything is working perfectly!** 🎉

