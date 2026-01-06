// ExamSphere - Security Features with AI Proctoring

const ExamSecurity = {
    violations: 0,
    maxViolations: 5,
    isExamActive: false,

    // Proctoring state
    proctorSessionId: null,
    videoStream: null,
    videoElement: null,
    canvasElement: null,
    frameInterval: null,

    init: async function (examId) {
        this.isExamActive = true;
        this.violations = 0;

        // Basic security
        this.disableRightClick();
        this.disableCopyPaste();
        this.disableRefresh();
        this.detectTabSwitch();
        this.detectWindowBlur();

        // AI Proctoring
        await this.initProctoring(examId);
    },

    // ==================== AI PROCTORING ====================

    initProctoring: async function (examId) {
        try {
            // Request camera permission
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });

            // Create video element
            this.videoElement = document.createElement('video');
            this.videoElement.srcObject = this.videoStream;
            this.videoElement.autoplay = true;
            this.videoElement.muted = true;

            // Create canvas for frame capture
            this.canvasElement = document.createElement('canvas');
            this.canvasElement.width = 640;
            this.canvasElement.height = 480;

            // Show camera preview
            this.showCameraPreview();

            // Wait for video to be ready
            await new Promise(resolve => {
                this.videoElement.onloadedmetadata = resolve;
            });

            // Wait 2 seconds for camera to warm up and user to position face
            this.showProctorStatus('warming');
            console.log('Camera warming up... Please position your face');
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Start proctoring session
            await this.startProctorSession(examId);

            // Start frame analysis (every 2 seconds)
            this.frameInterval = setInterval(() => {
                this.analyzeFrame();
            }, 2000);

            this.showProctorStatus('active');

        } catch (error) {
            console.error('Camera access error:', error);
            Utils.showAlert(
                'Camera access is required for this exam. Please allow camera access and refresh the page.',
                'danger',
                'examAlertContainer'
            );
            this.showProctorStatus('error');
        }
    },

    showCameraPreview: function () {
        // Create camera preview container
        const preview = document.createElement('div');
        preview.id = 'cameraPreview';
        preview.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 200px;
            height: 150px;
            border: 3px solid #28a745;
            border-radius: 8px;
            overflow: hidden;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        `;

        const video = this.videoElement.cloneNode(true);
        video.srcObject = this.videoStream;
        video.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';

        preview.appendChild(video);
        document.body.appendChild(preview);
    },

    showProctorStatus: function (status) {
        let statusDiv = document.getElementById('proctorStatus');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'proctorStatus';
            statusDiv.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            document.body.appendChild(statusDiv);
        }

        if (status === 'warming') {
            statusDiv.style.background = '#ffc107';
            statusDiv.style.color = 'black';
            statusDiv.innerHTML = '<i class="bi bi-camera-video"></i> Camera Initializing... Position your face';
        } else if (status === 'active') {
            statusDiv.style.background = '#28a745';
            statusDiv.style.color = 'white';
            statusDiv.innerHTML = '<i class="bi bi-camera-video-fill"></i> Proctoring Active';
        } else if (status === 'error') {
            statusDiv.style.background = '#dc3545';
            statusDiv.style.color = 'white';
            statusDiv.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> Camera Error';
        }
    },

    startProctorSession: async function (examId) {
        try {
            // Capture initial frame
            const blob = await this.captureFrame();

            // Create form data
            const formData = new FormData();
            formData.append('exam_id', examId);
            formData.append('frame', blob, 'initial.jpg');

            // Call backend
            const response = await fetch('http://localhost:8000/api/proctor/start', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${Utils.getAuthToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start proctoring');
            }

            const data = await response.json();
            this.proctorSessionId = data.session_id;

            console.log('Proctoring session started:', this.proctorSessionId);

        } catch (error) {
            console.error('Error starting proctor session:', error);
            Utils.showAlert(
                'Failed to start proctoring: ' + error.message,
                'danger',
                'examAlertContainer'
            );
        }
    },

    captureFrame: async function () {
        const ctx = this.canvasElement.getContext('2d');
        ctx.drawImage(this.videoElement, 0, 0, 640, 480);

        return new Promise(resolve => {
            this.canvasElement.toBlob(resolve, 'image/jpeg', 0.8);
        });
    },

    analyzeFrame: async function () {
        if (!this.proctorSessionId || !this.isExamActive) return;

        try {
            const blob = await this.captureFrame();

            const formData = new FormData();
            formData.append('session_id', this.proctorSessionId);
            formData.append('frame', blob, 'frame.jpg');

            const response = await fetch('http://localhost:8000/api/proctor/frame', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${Utils.getAuthToken()}`
                },
                body: formData
            });

            if (!response.ok) return;

            const data = await response.json();

            // Handle violations
            if (data.violation) {
                this.handleProctorViolation(data);
            }

        } catch (error) {
            console.error('Frame analysis error:', error);
        }
    },

    handleProctorViolation: function (data) {
        const violationMessages = {
            'LEFT_SEAT': 'Face not visible! Please stay in front of the camera.',
            'MULTIPLE_FACES': 'Multiple faces detected! Only you should be visible.',
            'CAMERA_COVERED': 'Camera appears to be covered. Please uncover it.',
            'IMPERSONATION': 'Identity verification failed! This is a serious violation.',
            'SPOOF_ATTACK': 'Suspicious activity detected (possible photo/video replay).'
        };

        const message = violationMessages[data.violation] || `Violation: ${data.violation}`;

        // Update violation count
        this.violations = data.total_violations;
        const violationsDisplay = document.getElementById('violationsCount');
        if (violationsDisplay) {
            violationsDisplay.textContent = this.violations;
        }

        // Show alert based on action
        if (data.action === 'TERMINATE_EXAM') {
            Utils.showAlert(
                `EXAM TERMINATED: ${message} (${this.violations} violations)`,
                'danger',
                'examAlertContainer'
            );
            this.autoSubmit('Too many proctoring violations');
        } else if (data.action === 'FINAL_WARNING') {
            Utils.showAlert(
                `FINAL WARNING: ${message} (${this.violations}/${this.maxViolations} violations)`,
                'danger',
                'examAlertContainer'
            );
        } else {
            Utils.showAlert(
                `WARNING: ${message} (${this.violations}/${this.maxViolations} violations)`,
                'warning',
                'examAlertContainer'
            );
        }
    },

    reportUIViolation: async function (violationType) {
        if (!this.proctorSessionId) return;

        try {
            await fetch('http://localhost:8000/api/proctor/ui', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${Utils.getAuthToken()}`
                },
                body: JSON.stringify({
                    session_id: this.proctorSessionId,
                    violation: violationType
                })
            });
        } catch (error) {
            console.error('Error reporting UI violation:', error);
        }
    },

    // ==================== BASIC SECURITY ====================

    disableRightClick: function () {
        document.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            ExamSecurity.recordViolation('Right-click detected');
            return false;
        });
    },

    disableCopyPaste: function () {
        document.addEventListener('copy', function (e) {
            e.preventDefault();
            ExamSecurity.recordViolation('Copy attempt detected');
            return false;
        });

        document.addEventListener('paste', function (e) {
            e.preventDefault();
            ExamSecurity.recordViolation('Paste attempt detected');
            return false;
        });

        document.addEventListener('cut', function (e) {
            e.preventDefault();
            ExamSecurity.recordViolation('Cut attempt detected');
            return false;
        });

        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x' || e.key === 'a')) {
                e.preventDefault();
                ExamSecurity.recordViolation('Keyboard shortcut detected');
                return false;
            }
        });
    },

    disableRefresh: function () {
        window.addEventListener('beforeunload', function (e) {
            if (ExamSecurity.isExamActive) {
                e.preventDefault();
                e.returnValue = 'Are you sure you want to leave? Your exam will be auto-submitted.';
                return e.returnValue;
            }
        });
    },

    detectTabSwitch: function () {
        document.addEventListener('visibilitychange', function () {
            if (document.hidden && ExamSecurity.isExamActive) {
                ExamSecurity.recordViolation('Tab switch detected');
                ExamSecurity.reportUIViolation('TAB_SWITCH');
            }
        });
    },

    detectWindowBlur: function () {
        window.addEventListener('blur', function () {
            if (ExamSecurity.isExamActive) {
                ExamSecurity.recordViolation('Window focus lost');
                ExamSecurity.reportUIViolation('WINDOW_BLUR');
            }
        });
    },

    recordViolation: function (reason) {
        if (!this.isExamActive) return;

        this.violations++;

        const violationsDisplay = document.getElementById('violationsCount');
        if (violationsDisplay) {
            violationsDisplay.textContent = this.violations;
        }

        Utils.showAlert(
            `Warning: ${reason}. Violations: ${this.violations}/${this.maxViolations}`,
            'warning',
            'examAlertContainer'
        );

        if (this.violations >= this.maxViolations) {
            this.autoSubmit('Multiple violations detected');
        }
    },

    autoSubmit: function (reason) {
        this.isExamActive = false;

        Utils.showAlert(
            `Exam auto-submitted due to: ${reason}`,
            'danger',
            'examAlertContainer'
        );

        setTimeout(() => {
            const submitBtn = document.getElementById('submitExamBtn');
            if (submitBtn) {
                submitBtn.click();
            } else {
                window.location.href = '/student/submission.html?type=auto';
            }
        }, 2000);
    },

    cleanup: function () {
        this.isExamActive = false;

        // Stop frame analysis
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
        }

        // Stop video stream
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
        }

        // Remove camera preview
        const preview = document.getElementById('cameraPreview');
        if (preview) {
            preview.remove();
        }

        // Remove proctor status
        const status = document.getElementById('proctorStatus');
        if (status) {
            status.remove();
        }
    }
};
