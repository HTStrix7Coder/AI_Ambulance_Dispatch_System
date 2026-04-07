import React, { useState, useEffect } from "react";
import { Heart, User, Phone, MapPin, FileText, AlertCircle, CheckCircle2, Clock, Stethoscope, Mic, StopCircle } from "lucide-react";
import { triageCase } from "./services/api";

export default function CaseForm() {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "M",
    contact: "",
    symptoms: "",
    location: ""
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await triageCase(formData);
      setResult(res.data);
    } catch (err) {
      setError("Failed to submit case. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTriageBadgeStyle = (level) => {
    switch(level) {
      case 'Emergency':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Transport':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Clinical':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  useEffect(() => {
    // Check for browser support
    if (!('webkitSpeechRecognition' in window)) {
        console.warn("Web Speech API is not supported by this browser.");
        return;
    }
    
    // Initialize speech recognition
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        setFormData(prev => ({
            ...prev,
            symptoms: finalTranscript + interimTranscript
        }));
    };

    recognition.onstart = () => {
        setIsRecording(true);
    };

    recognition.onend = () => {
        setIsRecording(false);
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        setError("Error during transcription. Please try again.");
    };

    const handleRecordToggle = () => {
        if (isRecording) {
            recognition.stop();
        } else {
            finalTranscript = ''; // Reset transcript before new recording
            recognition.start();
        }
    };
    
    window.handleRecordToggle = handleRecordToggle;

    // Cleanup function
    return () => {
        if (isRecording) {
            recognition.stop();
        }
    };
  }, []);

  return (
    <div className="container-fluid p-0" style={{ background: 'linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%)', minHeight: '100%' }}>
      <div className="mx-auto" style={{ maxWidth: 700 }}>
        {/* Header */}
        <div className="text-center mb-4">
          <div className="d-flex align-items-center justify-content-center mb-3">
            <div className="bg-primary p-3 rounded-circle me-3 d-flex align-items-center justify-content-center">
              <Stethoscope size={32} color="#fff" />
            </div>
            <div>
              <h1 className="h3 fw-bold text-dark mb-0">Medical Triage System</h1>
              <p className="text-muted mt-1 mb-0">Patient Case Intake & Assessment</p>
            </div>
          </div>
        </div>

        <div className="card shadow border-0 mb-4">
          {/* Form Header */}
          <div className="card-header text-white" style={{ background: 'linear-gradient(90deg, #007bff 0%, #00c6ff 100%)' }}>
            <h2 className="h5 mb-0 d-flex align-items-center">
              <FileText size={22} className="me-2" />
              New Patient Case Intake
            </h2>
            <p className="mb-0 mt-1" style={{ color: '#dbeafe', fontSize: 14 }}>Please fill in all required information for proper triage assessment</p>
          </div>

          <div className="card-body">
            <form onSubmit={handleSubmit}>
              {/* Patient Information Section */}
              <div className="border-start border-4 border-primary ps-3 mb-4">
                <h3 className="h6 fw-semibold text-dark mb-3 d-flex align-items-center">
                  <User size={18} className="me-2 text-primary" />
                  Patient Information
                </h3>
                <div className="row g-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      <User size={15} className="me-1 text-secondary" /> Full Name *
                    </label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Enter patient's full name" className="form-control" required />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Age *</label>
                    <input type="number" name="age" value={formData.age} onChange={handleChange} placeholder="Age in years" className="form-control" required />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Gender *</label>
                    <select name="gender" value={formData.gender} onChange={handleChange} className="form-select" required>
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                      <option value="O">Other</option>
                      <option value="P">Prefer not to say</option>
                    </select>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      <Phone size={15} className="me-1 text-secondary" /> Contact Number *
                    </label>
                    <input type="tel" name="contact" value={formData.contact} onChange={handleChange} placeholder="+91 XXXXX XXXXX" className="form-control" required />
                  </div>
                </div>
                <div className="mt-3">
                  <label className="form-label fw-semibold">
                    <MapPin size={15} className="me-1 text-secondary" /> Location *
                  </label>
                  <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Patient's current location (Address/Hospital/Clinic)" className="form-control" required />
                </div>
              </div>

              {/* Medical Information Section */}
              <div className="border-start border-4 border-danger ps-3 mb-4">
                <h3 className="h6 fw-semibold text-dark mb-3 d-flex align-items-center">
                  <Heart size={18} className="me-2 text-danger" /> Medical Assessment
                </h3>
                <div className="mb-2">
                  <label className="form-label fw-semibold">
                    <AlertCircle size={15} className="me-1 text-secondary" /> Chief Complaint & Symptoms *
                  </label>
                  <textarea name="symptoms" value={formData.symptoms} onChange={handleChange} placeholder="Describe the patient's primary complaint and symptoms in detail. Include onset, duration, severity, and any associated symptoms..." rows={4} className="form-control" required />
                  <div className="form-text">Be as specific as possible to ensure accurate triage assessment</div>
                </div>
                {/* Record Button */}
                <button type="button" onClick={() => window.handleRecordToggle()} className={`btn btn-${isRecording ? 'danger' : 'outline-secondary'} d-flex align-items-center mb-2`} style={{ borderRadius: 20 }}>
                  {isRecording ? <StopCircle size={16} className="me-2" /> : <Mic size={16} className="me-2" />}
                  {isRecording ? 'Stop Recording' : 'Record Symptoms'}
                </button>
              </div>

              {/* Submit Button */}
              <div className="pt-2">
                <button type="submit" disabled={loading} className={`btn btn-lg w-100 d-flex align-items-center justify-content-center ${loading ? 'btn-secondary' : 'btn-primary'}`} style={{ fontWeight: 600, borderRadius: 12 }}>
                  {loading ? (
                    <>
                      <Clock size={18} className="me-2 spinner-border spinner-border-sm" /> Processing Case...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 size={18} className="me-2" /> Submit for Triage Assessment
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Results Section */}
            {result && (
              <div className="alert alert-success mt-4">
                <div className="d-flex align-items-center mb-2">
                  <CheckCircle2 size={22} className="me-2 text-success" />
                  <h5 className="mb-0">Case Successfully Submitted</h5>
                </div>
                <div className="row g-2">
                  <div className="col-md-6">
                    <div className="bg-light rounded p-2 mb-2">
                      <div className="small text-muted">Case ID</div>
                      <div className="fw-bold text-primary">{result.id}</div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="bg-light rounded p-2 mb-2">
                      <div className="small text-muted">Patient Name</div>
                      <div className="fw-bold">{result.patient_name}</div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="bg-light rounded p-2 mb-2">
                      <div className="small text-muted">Triage Level</div>
                      <span className="badge bg-info text-dark">{result.triage_level}</span>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="bg-light rounded p-2 mb-2">
                      <div className="small text-muted">Status</div>
                      <div className="fw-bold text-warning">{result.status.replace('_', ' ')}</div>
                    </div>
                  </div>
                </div>
                <div className="bg-light rounded p-2 mb-2">
                  <div className="small text-muted">Symptoms Summary</div>
                  <div>{result.symptoms}</div>
                </div>
                <div className="alert alert-info mt-2 mb-0 p-2">
                  <strong>Next Steps:</strong> A medical professional will review this case and contact the patient within the appropriate timeframe based on the triage level assigned.
                </div>
              </div>
            )}

            {/* Error Section */}
            {error && (
              <div className="alert alert-danger mt-4 d-flex align-items-center">
                <AlertCircle size={20} className="me-2 text-danger" />
                <div>
                  <div className="fw-bold">Submission Failed</div>
                  <div>{error}</div>
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Footer */}
        <div className="text-center mt-3 text-muted small">
          Medical Triage System | Ensuring prompt and appropriate patient care
        </div>
      </div>
    </div>
  );
}

