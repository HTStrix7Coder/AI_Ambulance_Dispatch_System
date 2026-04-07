# VAPI 404 Error Troubleshooting Guide

## Error: "Your server rejected `tool-calls` webhook. Error: Request failed with status code 404"

This means VAPI cannot reach your endpoint. Follow these steps:

## ✅ Step 1: Verify Your Backend Server is Running

1. **Check if your FastAPI server is running:**
   ```bash
   # In your backend directory
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test locally:**
   Open browser: `http://localhost:8000/docs`
   - You should see the FastAPI docs
   - Look for `/vapi/tool-calls` endpoint

## ✅ Step 2: Verify ngrok is Running and Forwarding

1. **Check ngrok is running:**
   ```bash
   ngrok http 8000
   ```

2. **Verify the ngrok URL:**
   - Should show: `https://xxxxx.ngrok-free.dev -> http://localhost:8000`
   - Copy the HTTPS URL (e.g., `https://remunerative-neva-mitigate.ngrok-free.dev`)

3. **Test ngrok URL:**
   ```bash
   # Test the endpoint via ngrok
   curl https://remunerative-neva-mitigate.ngrok-free.dev/vapi/config
   ```
   - Should return JSON with VAPI configuration

## ✅ Step 3: Verify VAPI Dashboard URL

In VAPI Dashboard → Tools → Your Function Tool:

**Server URL should be:**
```
https://remunerative-neva-mitigate.ngrok-free.dev/vapi/tool-calls
```

**NOT:**
- ❌ `https://remunerative-neva-mitigate.ngrok-free.dev/vapi/function-call` (old endpoint)
- ❌ `http://localhost:8000/vapi/tool-calls` (localhost won't work)
- ❌ `https://remunerative-neva-mitigate.ngrok-free.dev/tool-calls` (missing /vapi)

## ✅ Step 4: Test Endpoint Directly

Test your endpoint via ngrok:

```bash
# Test tool-calls endpoint
curl -X POST https://remunerative-neva-mitigate.ngrok-free.dev/vapi/tool-calls \
  -H "Content-Type: application/json" \
  -d '{"test":"test"}'
```

**Expected response:**
- Should NOT return 404
- Should return JSON (even if it's an error about missing parameters)

## ✅ Step 5: Check Backend Logs

When you make a test call, check your backend console:

**You SHOULD see:**
```
🌐 INCOMING REQUEST: POST /vapi/tool-calls
🔔 VAPI FUNCTION CALL WEBHOOK RECEIVED
```

**If you DON'T see this:**
- The request isn't reaching your server
- Check ngrok URL is correct
- Check backend server is running

## ✅ Step 6: Common Issues

### Issue 1: ngrok URL Changed
- Free ngrok URLs change every time you restart ngrok
- **Solution:** Update VAPI dashboard with new ngrok URL

### Issue 2: ngrok Free Tier Warning Page
- Free ngrok shows a warning page
- **Solution:** 
  - Upgrade to paid ngrok, OR
  - Add `ngrok-skip-browser-warning` header in VAPI (if supported), OR
  - Use ngrok's static domain feature

### Issue 3: Backend Server Not Running
- **Solution:** Start your FastAPI server

### Issue 4: Wrong Port
- ngrok should forward to port 8000
- **Solution:** `ngrok http 8000` (not 3000, 5000, etc.)

### Issue 5: Firewall Blocking
- **Solution:** Check firewall allows port 8000

## ✅ Step 7: Verify Route Registration

Check your `backend/app/main.py`:

```python
app.include_router(vapi.router, tags=["vapi"])
```

And `backend/app/routers/vapi.py`:

```python
@router.post("/vapi/tool-calls")
async def handle_vapi_function_call(request: Request):
    ...
```

## 🔍 Quick Debug Checklist

- [ ] Backend server running on port 8000?
- [ ] ngrok running and forwarding to port 8000?
- [ ] ngrok URL is HTTPS (not HTTP)?
- [ ] VAPI dashboard URL includes `/vapi/tool-calls`?
- [ ] VAPI dashboard URL uses ngrok URL (not localhost)?
- [ ] Can access `https://your-ngrok-url.ngrok-free.dev/vapi/config`?
- [ ] Backend logs show incoming requests?

## 📞 Still Not Working?

1. **Check ngrok web interface:**
   - Open: `http://127.0.0.1:4040`
   - See if requests are reaching ngrok

2. **Check VAPI logs:**
   - VAPI Dashboard → Logs
   - See what error VAPI is getting

3. **Test with Postman/curl:**
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.dev/vapi/tool-calls \
     -H "Content-Type: application/json" \
     -d '{"toolCalls":[{"id":"test","name":"create_emergency_case","parameters":{}}]}'
   ```

4. **Check backend console for errors:**
   - Look for any Python exceptions
   - Check if routes are registered

