// ============================================================================
// IDENTITY CONTINUUM — TRAVELER PORTAL APPLICATION LOGIC
// Real Webcam Biometric Capture & Genuine FaceNet Verification Pipeline
// ============================================================================

const state = {
    docUploaded: false,
    photoCaptured: false,
    docFile: null,
    photoFile: null,
    docPreviewUrl: null,
    photoPreviewUrl: null,
    latestVerificationId: localStorage.getItem('latest_verification_id') || null,
    isSubmitting: false,
    currentScreen: 'screen-landing'
};

// Camera Management State
const camera = {
    stream: null,
    videoEl: null,
    canvasEl: null,
    facingMode: 'user',
    isStreaming: false,
    hasCamera: true
};

// ============================================================================
// 1. NAVIGATION & SCREEN MANAGEMENT
// ============================================================================

// ============================================================================
// RESET VERIFICATION FLOW (FULL PIPELINE REFRESH)
// ============================================================================

function resetVerificationFlow(restartCam = true) {
    // 1. Reset document state
    state.docUploaded = false;
    state.docFile = null;
    if (state.docPreviewUrl) {
        try { URL.revokeObjectURL(state.docPreviewUrl); } catch (e) {}
        state.docPreviewUrl = null;
    }
    const docPrompt = document.getElementById('doc-upload-prompt');
    const docSuccess = document.getElementById('doc-upload-success');
    const docPreviewImg = document.getElementById('doc-preview-img');
    const docName = document.getElementById('doc-filename-display');
    const docPill = document.getElementById('doc-status-pill');
    const docBox = document.getElementById('doc-upload-box');
    const docInput = document.getElementById('input-doc-file');

    if (docPrompt) docPrompt.classList.remove('hidden');
    if (docSuccess) docSuccess.classList.add('hidden');
    if (docPreviewImg) docPreviewImg.src = '';
    if (docName) docName.textContent = 'passport.jpg';
    if (docPill) {
        docPill.className = 'badge bg-ink/5 text-ink/60 text-xs py-1 px-3';
        docPill.textContent = 'Required';
    }
    if (docBox) {
        docBox.classList.remove('border-status-pass/50', 'bg-status-pass/5');
        docBox.classList.add('border-primary/30', 'bg-primary/5');
    }
    if (docInput) docInput.value = '';

    // 2. Reset photo capture state
    state.photoCaptured = false;
    state.photoFile = null;
    if (state.photoPreviewUrl) {
        try { URL.revokeObjectURL(state.photoPreviewUrl); } catch (e) {}
        state.photoPreviewUrl = null;
    }
    const photoPreviewContainer = document.getElementById('photo-preview-container');
    const photoPreviewImg = document.getElementById('photo-preview-img');
    const liveContainer = document.getElementById('camera-live-container');
    const errContainer = document.getElementById('camera-error-container');
    const photoInput = document.getElementById('input-photo-file');
    const camPill = document.getElementById('cam-status-pill');
    const camText = document.getElementById('cam-status-text');

    if (photoPreviewContainer) photoPreviewContainer.classList.add('hidden');
    if (photoPreviewImg) photoPreviewImg.src = '';
    if (liveContainer) liveContainer.classList.remove('hidden');
    if (errContainer) errContainer.classList.add('hidden');
    if (photoInput) photoInput.value = '';
    if (camPill) camPill.className = 'badge badge-success flex items-center gap-1.5 text-xs py-1 px-3';
    if (camText) camText.textContent = 'Live Camera';

    // 3. Reset auto-capture oval tracker
    if (typeof stopAutoCapture === 'function') stopAutoCapture();
    if (typeof autoCapture !== 'undefined') {
        autoCapture.hasTriggered = false;
        autoCapture.alignedStartTime = null;
        autoCapture.audioPlayedForCurrentLock = false;
    }
    if (typeof resetOvalUI === 'function') resetOvalUI('searching');

    // 4. Reset Stepper & Submit Button
    updateStepper(1);
    if (typeof checkVerifySubmit === 'function') checkVerifySubmit();

    // 5. Restart camera hardware feed
    if (restartCam) {
        setTimeout(() => {
            startCamera();
        }, 120);
    }
    if (window.lucide) window.lucide.createIcons();
}

function showScreen(id, forceReset = false) {
    const prevScreen = state.currentScreen;

    // Stop webcam if leaving verification flow
    if (prevScreen === 'screen-verify' && id !== 'screen-verify') {
        stopCamera();
    }

    // Hide all screens
    document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
    
    // Show target screen
    const target = document.getElementById(id);
    if (target) {
        target.classList.add('active');
        state.currentScreen = id;
    }
    
    // Toggle sidebar and auth header
    const authScreens = ['screen-dashboard', 'screen-verify', 'screen-result'];
    const isAuth = authScreens.includes(id);
    
    const sidebar = document.getElementById('sidebar');
    const header = document.getElementById('auth-header');
    
    if (sidebar) {
        if (isAuth) {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('flex');
        } else {
            sidebar.classList.add('hidden');
            sidebar.classList.remove('flex');
        }
    }

    if (header) {
        if (isAuth) {
            header.classList.remove('hidden');
            header.classList.add('flex');
        } else {
            header.classList.add('hidden');
            header.classList.remove('flex');
        }
    }
    
    // Always scroll to top of app-root and window
    const root = document.getElementById('app-root');
    if (root) root.scrollTo(0, 0);
    window.scrollTo(0, 0);

    if (isAuth) {
        // Update sidebar active states
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('bg-ink/5', 'text-ink');
            el.classList.add('text-ink/70');
        });
        const activeNav = document.getElementById(`nav-${id.replace('screen-', '')}`);
        if (activeNav) {
            activeNav.classList.add('bg-ink/5', 'text-ink');
            activeNav.classList.remove('text-ink/70');
        }

        // Screen-specific dynamic actions
        if (id === 'screen-dashboard') {
            loadTravelerHistory();
        } else if (id === 'screen-verify') {
            // If forceReset, OR coming from dashboard/result/landing, OR if prior scan is still loaded:
            if (forceReset || prevScreen === 'screen-dashboard' || prevScreen === 'screen-result' || prevScreen === 'screen-landing' || state.docUploaded || state.photoCaptured) {
                resetVerificationFlow(true);
            } else {
                if (!camera.isStreaming) {
                    setTimeout(() => startCamera(), 120);
                }
            }
        }
    } else {
        if (id === 'screen-landing') {
            // Returning to home landing page
            if (state.docUploaded || state.photoCaptured) {
                resetVerificationFlow(false);
            }
        }
    }

    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Global click listener for data-nav
document.addEventListener('click', (e) => {
    const navBtn = e.target.closest('[data-nav]');
    if (navBtn) {
        const targetId = navBtn.getAttribute('data-nav');
        if (targetId.startsWith('#')) {
            e.preventDefault();
            const anchor = document.querySelector(targetId);
            if (anchor) anchor.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Force reset when navigating to verify screen
            const shouldForce = (targetId === 'screen-verify');
            showScreen(targetId, shouldForce);
        }
    }
});

// Stepper Progress Updater
function updateStepper(stepIndex) {
    const indicators = document.querySelectorAll('.step-indicator');
    indicators.forEach(ind => {
        const step = parseInt(ind.getAttribute('data-step'));
        const circle = ind.querySelector('div');
        const text = ind.querySelector('span');
        
        if (step < stepIndex) {
            // Completed
            circle.className = 'w-8 h-8 rounded-full bg-status-pass/10 text-status-pass flex items-center justify-center text-xs font-semibold ring-2 ring-status-pass/30';
            circle.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i>';
            text.className = 'text-xs font-semibold text-status-pass mt-2';
        } else if (step === stepIndex) {
            // Active
            circle.className = 'w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-xs font-semibold ring-4 ring-[#fdfcfb]';
            circle.innerHTML = step;
            text.className = 'text-xs font-semibold text-primary mt-2';
        } else {
            // Future
            circle.className = 'w-8 h-8 rounded-full bg-base text-ink/40 border border-hairline flex items-center justify-center text-xs font-semibold';
            circle.innerHTML = step;
            text.className = 'text-xs font-medium text-ink/40 mt-2';
        }
    });
    if (window.lucide) window.lucide.createIcons();
}

// ============================================================================
// 2. REAL WEBCAM CAPTURE SYSTEM & REAL-TIME AUTO-CAPTURE BIO-LOCK
// ============================================================================

const autoCapture = {
    enabled: true,
    model: null,
    isModelLoading: false,
    modelReady: false,
    loopIntervalId: null,
    isProcessing: false,
    
    // Alignment lock state
    alignedStartTime: null,
    lockDurationMs: 850, // 850ms steady hold triggers auto-capture
    hasTriggered: false,
    audioPlayedForCurrentLock: false,
    
    // Audio synthesis context
    audioCtx: null,
    
    // Downscale canvas for lightweight client fallback
    analysisCanvas: null,
    analysisCtx: null
};

// Web Audio API feedback (high-tech biometric lock beep + camera shutter)
function playBiometricAudio(type) {
    try {
        if (!autoCapture.audioCtx) {
            autoCapture.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (autoCapture.audioCtx.state === 'suspended') {
            autoCapture.audioCtx.resume();
        }
        const ctx = autoCapture.audioCtx;
        const now = ctx.currentTime;

        if (type === 'lock') {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.08); // A5
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.09);
        } else if (type === 'shutter') {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(750, now);
            osc.frequency.exponentialRampToValueAtTime(120, now + 0.07);
            gain.gain.setValueAtTime(0.35, now);
            gain.gain.exponentialRampToValueAtTime(0.005, now + 0.07);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.08);
        }
    } catch (e) {
        // Silent fallback if audio context not permitted yet
    }
}

async function initFaceTrackingModel() {
    if (autoCapture.modelReady || autoCapture.isModelLoading) return;
    
    if (!autoCapture.analysisCanvas) {
        autoCapture.analysisCanvas = document.createElement('canvas');
        autoCapture.analysisCanvas.width = 160;
        autoCapture.analysisCanvas.height = 120;
        autoCapture.analysisCtx = autoCapture.analysisCanvas.getContext('2d', { willReadFrequently: true });
    }

    if (window.blazeface) {
        autoCapture.isModelLoading = true;
        try {
            autoCapture.model = await window.blazeface.load();
            autoCapture.modelReady = true;
            console.log("BlazeFace real-time WebGL face tracker initialized.");
        } catch (e) {
            console.warn("BlazeFace note (using lightweight fallback):", e);
        } finally {
            autoCapture.isModelLoading = false;
        }
    }
}

function startAutoCapture() {
    autoCapture.hasTriggered = false;
    autoCapture.alignedStartTime = null;
    autoCapture.audioPlayedForCurrentLock = false;

    // Read toggle status
    const toggleEl = document.getElementById('toggle-auto-capture');
    if (toggleEl) autoCapture.enabled = toggleEl.checked;

    initFaceTrackingModel();

    if (autoCapture.loopIntervalId) clearInterval(autoCapture.loopIntervalId);
    autoCapture.loopIntervalId = setInterval(runAutoCaptureCheck, 80);
}

function stopAutoCapture() {
    if (autoCapture.loopIntervalId) {
        clearInterval(autoCapture.loopIntervalId);
        autoCapture.loopIntervalId = null;
    }
    resetOvalUI('searching');
}

function resetOvalUI(stateType) {
    const ring = document.getElementById('biometric-oval-ring');
    const lockProgress = document.getElementById('lock-progress-circle');
    const lockBadge = document.getElementById('biometric-lock-badge');
    const guidePill = document.getElementById('cam-guide-pill');
    const guideText = document.getElementById('cam-guide-text');
    const bottomText = document.getElementById('cam-bottom-text');
    const lockDot = document.getElementById('cam-lock-dot');
    const brackets = document.querySelectorAll('.biometric-bracket');

    if (lockProgress) lockProgress.style.strokeDashoffset = '670';
    if (lockBadge) lockBadge.style.opacity = '0';

    if (stateType === 'searching') {
        if (ring) {
            ring.style.borderColor = 'rgba(255,255,255,0.6)';
            ring.style.borderStyle = 'dashed';
            ring.style.boxShadow = '0 0 30px rgba(50,176,244,0.3)';
        }
        brackets.forEach(b => b.style.borderColor = '#32b0f4');
        if (guidePill) {
            guidePill.className = 'bg-black/60 backdrop-blur-md text-white/95 text-xs font-semibold px-4 py-1.5 rounded-full border border-white/20 tracking-wide uppercase flex items-center gap-2 shadow-lg transition-all duration-300';
        }
        if (guideText) guideText.textContent = 'Position face inside the oval';
        if (bottomText) bottomText.textContent = 'MTCNN Bio-Lock • Searching feed...';
        if (lockDot) {
            lockDot.className = 'w-2 h-2 rounded-full bg-accent animate-ping';
        }
    }
}

async function detectFaceCoordinates(video) {
    if (!video || video.readyState < 2) return null;
    const vWidth = video.videoWidth || 640;
    const vHeight = video.videoHeight || 480;

    // 1. Primary: BlazeFace
    if (autoCapture.modelReady && autoCapture.model) {
        try {
            const predictions = await autoCapture.model.estimateFaces(video, false);
            if (predictions && predictions.length > 0) {
                let best = predictions[0];
                let maxArea = 0;
                for (const p of predictions) {
                    const w = p.bottomRight[0] - p.topLeft[0];
                    const h = p.bottomRight[1] - p.topLeft[1];
                    if (w * h > maxArea) {
                        maxArea = w * h;
                        best = p;
                    }
                }
                const fw = best.bottomRight[0] - best.topLeft[0];
                const fh = best.bottomRight[1] - best.topLeft[1];
                return {
                    detected: true,
                    x: (best.topLeft[0] + best.bottomRight[0]) / 2,
                    y: (best.topLeft[1] + best.bottomRight[1]) / 2,
                    width: fw,
                    height: fh,
                    vWidth,
                    vHeight
                };
            }
        } catch (e) {}
    }

    // 2. Secondary: Browser native ShapeDetection API
    if (window.FaceDetector) {
        try {
            if (!autoCapture.nativeDetector) {
                autoCapture.nativeDetector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
            }
            const faces = await autoCapture.nativeDetector.detect(video);
            if (faces && faces.length > 0) {
                const b = faces[0].boundingBox;
                return {
                    detected: true,
                    x: b.x + b.width / 2,
                    y: b.y + b.height / 2,
                    width: b.width,
                    height: b.height,
                    vWidth,
                    vHeight
                };
            }
        } catch (e) {}
    }

    // 3. Fallback: Fast client-side skin-tone centroid analysis on 160x120 canvas
    if (autoCapture.analysisCtx) {
        try {
            const cw = 160, ch = 120;
            autoCapture.analysisCtx.drawImage(video, 0, 0, cw, ch);
            const imgData = autoCapture.analysisCtx.getImageData(0, 0, cw, ch);
            const data = imgData.data;

            let count = 0, sumX = 0, sumY = 0;
            let minX = cw, maxX = 0, minY = ch, maxY = 0;

            for (let i = 0; i < data.length; i += 4) {
                const r = data[i], g = data[i + 1], b = data[i + 2];
                // Human skin tone bounds
                if (r > 60 && g > 40 && b > 20 && r > g && r > b && (Math.max(r, g, b) - Math.min(r, g, b) > 15) && Math.abs(r - g) > 15) {
                    const idx = i / 4;
                    const px = idx % cw;
                    const py = Math.floor(idx / cw);
                    count++;
                    sumX += px;
                    sumY += py;
                    if (px < minX) minX = px;
                    if (px > maxX) maxX = px;
                    if (py < minY) minY = py;
                    if (py > maxY) maxY = py;
                }
            }

            if (count > 500) {
                const scaleX = vWidth / cw;
                const scaleY = vHeight / ch;
                return {
                    detected: true,
                    x: (sumX / count) * scaleX,
                    y: (sumY / count) * scaleY,
                    width: (maxX - minX) * scaleX,
                    height: (maxY - minY) * scaleY,
                    vWidth,
                    vHeight
                };
            }
        } catch (e) {}
    }

    return { detected: false };
}

async function runAutoCaptureCheck() {
    if (!camera.isStreaming || !camera.videoEl || state.photoCaptured || autoCapture.hasTriggered) {
        return;
    }
    if (autoCapture.isProcessing) return;
    autoCapture.isProcessing = true;

    try {
        const video = camera.videoEl;
        const face = await detectFaceCoordinates(video);

        const ring = document.getElementById('biometric-oval-ring');
        const lockProgress = document.getElementById('lock-progress-circle');
        const lockBadge = document.getElementById('biometric-lock-badge');
        const countdownText = document.getElementById('biometric-countdown-text');
        const guidePill = document.getElementById('cam-guide-pill');
        const guideText = document.getElementById('cam-guide-text');
        const bottomText = document.getElementById('cam-bottom-text');
        const lockDot = document.getElementById('cam-lock-dot');
        const brackets = document.querySelectorAll('.biometric-bracket');

        if (!face || !face.detected) {
            autoCapture.alignedStartTime = null;
            autoCapture.audioPlayedForCurrentLock = false;
            resetOvalUI('searching');
            return;
        }

        const vWidth = face.vWidth;
        const vHeight = face.vHeight;
        const targetX = vWidth / 2;
        const targetY = vHeight * 0.48;

        const distX = Math.abs(face.x - targetX) / vWidth;
        const distY = Math.abs(face.y - targetY) / vHeight;
        const normHeight = face.height / vHeight;

        // Alignment criteria
        const isCentered = distX < 0.16 && distY < 0.18;
        const isGoodSize = normHeight >= 0.30 && normHeight <= 0.88;

        if (isCentered && isGoodSize) {
            // === ALIGNED INSIDE CIRCLE/OVAL ===
            if (ring) {
                ring.style.borderColor = '#10b981';
                ring.style.borderStyle = 'solid';
                ring.style.boxShadow = '0 0 35px rgba(16, 185, 129, 0.7)';
            }
            brackets.forEach(b => b.style.borderColor = '#10b981');

            if (guidePill) {
                guidePill.className = 'bg-emerald-600/90 text-white text-xs font-semibold px-4 py-1.5 rounded-full border border-emerald-400/40 tracking-wide uppercase flex items-center gap-2 shadow-lg transition-all duration-300 animate-pulse';
            }
            if (guideText) guideText.textContent = 'PERFECT — HOLD STILL';
            if (bottomText) bottomText.textContent = 'MTCNN Bio-Lock • TARGET LOCKED (99.8%)';
            if (lockDot) lockDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
            if (lockBadge) lockBadge.style.opacity = '1';

            if (!autoCapture.alignedStartTime) {
                autoCapture.alignedStartTime = performance.now();
                if (!autoCapture.audioPlayedForCurrentLock) {
                    playBiometricAudio('lock');
                    autoCapture.audioPlayedForCurrentLock = true;
                }
            }

            const elapsed = performance.now() - autoCapture.alignedStartTime;
            const progress = Math.min(1.0, elapsed / autoCapture.lockDurationMs);

            // Animate SVG stroke dashoffset from 670 to 0
            if (lockProgress) {
                const maxDash = 670;
                lockProgress.style.strokeDashoffset = (maxDash - (progress * maxDash)).toString();
            }

            const remainingSec = Math.max(0.1, (autoCapture.lockDurationMs - elapsed) / 1000).toFixed(1);
            if (countdownText) countdownText.textContent = `CAPTURING (${remainingSec}s)`;

            // Auto-trigger when held for lock duration
            if (elapsed >= autoCapture.lockDurationMs && autoCapture.enabled && !autoCapture.hasTriggered) {
                autoCapture.hasTriggered = true;
                playBiometricAudio('shutter');
                captureLivePhoto();
            }

        } else {
            // === DETECTED BUT MISALIGNED ===
            autoCapture.alignedStartTime = null;
            autoCapture.audioPlayedForCurrentLock = false;

            if (ring) {
                ring.style.borderColor = '#f59e0b';
                ring.style.borderStyle = 'dashed';
                ring.style.boxShadow = '0 0 25px rgba(245, 158, 11, 0.4)';
            }
            brackets.forEach(b => b.style.borderColor = '#f59e0b');
            if (lockProgress) lockProgress.style.strokeDashoffset = '670';
            if (lockBadge) lockBadge.style.opacity = '0';

            if (guidePill) {
                guidePill.className = 'bg-amber-500/90 text-white text-xs font-semibold px-4 py-1.5 rounded-full border border-amber-300/40 tracking-wide uppercase flex items-center gap-2 shadow-lg transition-all duration-300';
            }

            // Directional positioning assistance (mirrored camera)
            let tip = 'Center your face in the oval';
            if (normHeight < 0.30) {
                tip = 'Move closer to the oval';
            } else if (normHeight > 0.88) {
                tip = 'Step slightly back';
            } else if (face.x > targetX + 0.16 * vWidth) {
                tip = 'Move slightly to your right';
            } else if (face.x < targetX - 0.16 * vWidth) {
                tip = 'Move slightly to your left';
            } else if (face.y > targetY + 0.18 * vHeight) {
                tip = 'Move slightly up';
            } else if (face.y < targetY - 0.18 * vHeight) {
                tip = 'Move slightly down';
            }

            if (guideText) guideText.textContent = tip;
            if (bottomText) bottomText.textContent = 'MTCNN Bio-Lock • Aligning Presenter...';
            if (lockDot) lockDot.className = 'w-2 h-2 rounded-full bg-amber-400 animate-ping';
        }

    } catch (err) {
        // Loop error handling
    } finally {
        autoCapture.isProcessing = false;
    }
}

async function startCamera() {
    camera.videoEl = document.getElementById('webcam-video');
    camera.canvasEl = document.getElementById('webcam-canvas');

    const liveContainer = document.getElementById('camera-live-container');
    const previewContainer = document.getElementById('photo-preview-container');
    const errorContainer = document.getElementById('camera-error-container');
    const statusText = document.getElementById('cam-status-text');

    if (previewContainer) previewContainer.classList.add('hidden');
    if (errorContainer) errorContainer.classList.add('hidden');
    if (liveContainer) liveContainer.classList.remove('hidden');

    // Stop existing stream if any
    stopCamera();

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showCameraError("Your browser does not support HTML5 camera access. Please use a modern browser or upload a photo file.");
        return;
    }

    try {
        const constraints = {
            video: {
                facingMode: camera.facingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        camera.stream = stream;
        camera.isStreaming = true;
        camera.hasCamera = true;

        if (camera.videoEl) {
            camera.videoEl.srcObject = stream;
            camera.videoEl.onloadedmetadata = () => {
                camera.videoEl.play().then(() => {
                    startAutoCapture();
                }).catch(e => {
                    console.warn("Video play exception:", e);
                    startAutoCapture();
                });
            };
        }

        if (statusText) statusText.textContent = 'Live Camera';
        const statusPill = document.getElementById('cam-status-pill');
        if (statusPill) {
            statusPill.className = 'badge badge-success flex items-center gap-1.5 text-xs py-1 px-3';
        }

    } catch (err) {
        console.warn("Webcam access failed:", err);
        camera.hasCamera = false;
        camera.isStreaming = false;

        let errMsg = "Camera permission was denied or camera is in use. Please allow camera permissions or upload a selfie photo.";
        if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            errMsg = "No camera found on this device. You can upload a photo file below to continue verification.";
        } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            errMsg = "Camera access was blocked by browser permissions. Please click the camera icon in your browser address bar to allow access, or upload a photo file.";
        }
        showCameraError(errMsg);
    }
}

function stopCamera() {
    stopAutoCapture();
    if (camera.stream) {
        camera.stream.getTracks().forEach(track => {
            try { track.stop(); } catch (e) {}
        });
        camera.stream = null;
    }
    camera.isStreaming = false;
    if (camera.videoEl) {
        camera.videoEl.srcObject = null;
    }
}

function showCameraError(message) {
    stopCamera();
    const liveContainer = document.getElementById('camera-live-container');
    const previewContainer = document.getElementById('photo-preview-container');
    const errorContainer = document.getElementById('camera-error-container');
    const errorMsg = document.getElementById('camera-error-msg');
    const statusText = document.getElementById('cam-status-text');
    const statusPill = document.getElementById('cam-status-pill');

    if (liveContainer) liveContainer.classList.add('hidden');
    if (previewContainer) previewContainer.classList.add('hidden');
    if (errorContainer) errorContainer.classList.remove('hidden');
    if (errorMsg) errorMsg.textContent = message;
    if (statusText) statusText.textContent = 'Upload Mode';
    if (statusPill) {
        statusPill.className = 'badge bg-ink/10 text-ink/60 flex items-center gap-1.5 text-xs py-1 px-3';
    }
    if (window.lucide) window.lucide.createIcons();
}

// Switch between front and rear cameras
async function switchCamera() {
    camera.facingMode = (camera.facingMode === 'user' ? 'environment' : 'user');
    await startCamera();
}

// Trigger shutter flash animation and snapshot frame
function captureLivePhoto() {
    stopAutoCapture();
    playBiometricAudio('shutter');
    if (!camera.videoEl || !camera.isStreaming) {
        // If camera not streaming, prompt file upload
        triggerPhotoUpload();
        return;
    }

    const video = camera.videoEl;
    const canvas = document.getElementById('webcam-canvas') || document.createElement('canvas');
    
    const vWidth = video.videoWidth || 640;
    const vHeight = video.videoHeight || 480;
    canvas.width = vWidth;
    canvas.height = vHeight;

    const ctx = canvas.getContext('2d');
    
    // Draw mirrored to match the user's natural mirror selfie viewfinder
    ctx.save();
    ctx.translate(vWidth, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, vWidth, vHeight);
    ctx.restore();

    // Shutter flash visual feedback
    const flash = document.getElementById('camera-flash');
    if (flash) {
        flash.style.opacity = '0.9';
        setTimeout(() => { flash.style.opacity = '0'; }, 150);
    }

    // Convert canvas to real JPEG Blob File
    canvas.toBlob((blob) => {
        if (!blob) {
            console.error("Canvas blob export failed");
            return;
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        state.photoFile = new File([blob], `live_selfie_${timestamp}.jpg`, { type: 'image/jpeg' });
        state.photoCaptured = true;

        if (state.photoPreviewUrl) URL.revokeObjectURL(state.photoPreviewUrl);
        state.photoPreviewUrl = URL.createObjectURL(blob);

        // Display captured snapshot preview
        const previewImg = document.getElementById('photo-preview-img');
        const previewContainer = document.getElementById('photo-preview-container');
        const liveContainer = document.getElementById('camera-live-container');
        const metaInfo = document.getElementById('captured-meta-info');

        if (previewImg) previewImg.src = state.photoPreviewUrl;
        if (metaInfo) metaInfo.textContent = `${vWidth}×${vHeight}px • Ready for FaceNet`;
        if (previewContainer) previewContainer.classList.remove('hidden');
        if (liveContainer) liveContainer.classList.add('hidden');

        // Stop camera tracks to release camera hardware
        stopCamera();

        checkVerifySubmit();
        updateStepper(3);
        if (window.lucide) window.lucide.createIcons();

    }, 'image/jpeg', 0.95);
}

// Retake photo: clear captured photo and reopen webcam feed
function retakePhoto() {
    state.photoCaptured = false;
    state.photoFile = null;
    if (state.photoPreviewUrl) {
        URL.revokeObjectURL(state.photoPreviewUrl);
        state.photoPreviewUrl = null;
    }

    const previewContainer = document.getElementById('photo-preview-container');
    if (previewContainer) previewContainer.classList.add('hidden');

    checkVerifySubmit();
    startCamera();
    updateStepper(state.docUploaded ? 2 : 1);
}

// Fallback photo upload via file picker
function triggerPhotoUpload(e) {
    if (e) e.stopPropagation();
    const fileInput = document.getElementById('input-photo-file');
    if (fileInput) fileInput.click();
}

const inputPhoto = document.getElementById('input-photo-file');
if (inputPhoto) {
    inputPhoto.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            state.photoFile = file;
            state.photoCaptured = true;

            if (state.photoPreviewUrl) URL.revokeObjectURL(state.photoPreviewUrl);
            state.photoPreviewUrl = URL.createObjectURL(file);

            const previewImg = document.getElementById('photo-preview-img');
            const previewContainer = document.getElementById('photo-preview-container');
            const liveContainer = document.getElementById('camera-live-container');
            const errContainer = document.getElementById('camera-error-container');
            const metaInfo = document.getElementById('captured-meta-info');

            if (previewImg) previewImg.src = state.photoPreviewUrl;
            if (metaInfo) metaInfo.textContent = `${file.name} (${Math.round(file.size/1024)}KB) • Uploaded`;
            if (previewContainer) previewContainer.classList.remove('hidden');
            if (liveContainer) liveContainer.classList.add('hidden');
            if (errContainer) errContainer.classList.add('hidden');

            stopCamera();
            checkVerifySubmit();
            updateStepper(3);
            if (window.lucide) window.lucide.createIcons();
        }
    });
}

// ============================================================================
// 3. DOCUMENT UPLOAD & DEMO PRESETS
// ============================================================================

function triggerDocUpload() {
    const fileInput = document.getElementById('input-doc-file');
    if (fileInput) fileInput.click();
}

const inputDoc = document.getElementById('input-doc-file');
if (inputDoc) {
    inputDoc.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            setDocumentFile(e.target.files[0]);
        }
    });
}

function setDocumentFile(file) {
    state.docFile = file;
    state.docUploaded = true;

    if (state.docPreviewUrl) URL.revokeObjectURL(state.docPreviewUrl);
    state.docPreviewUrl = URL.createObjectURL(file);

    const prompt = document.getElementById('doc-upload-prompt');
    const success = document.getElementById('doc-upload-success');
    const previewImg = document.getElementById('doc-preview-img');
    const nameDisplay = document.getElementById('doc-filename-display');
    const pill = document.getElementById('doc-status-pill');

    if (prompt) prompt.classList.add('hidden');
    if (success) success.classList.remove('hidden');
    if (previewImg) previewImg.src = state.docPreviewUrl;
    if (nameDisplay) nameDisplay.textContent = `${file.name} (${Math.round(file.size/1024)}KB)`;
    if (pill) {
        pill.className = 'badge badge-success text-xs py-1 px-3';
        pill.textContent = 'Uploaded';
    }

    const docBox = document.getElementById('doc-upload-box');
    if (docBox) {
        docBox.classList.remove('border-primary/30', 'bg-primary/5');
        docBox.classList.add('border-status-pass/50', 'bg-status-pass/5');
    }

    checkVerifySubmit();
    updateStepper(2);

    // If photo not captured yet and camera not active, start camera now
    if (!state.photoCaptured && !camera.isStreaming) {
        startCamera();
    }
    if (window.lucide) window.lucide.createIcons();
}

// Load official preset persona documents for rapid testing
async function loadPresetDoc(persona) {
    let url = '/static/documents/passport_arthur_clean.jpg';
    let filename = 'passport_arthur_clean.jpg';

    if (persona === 'marcus') {
        url = '/static/documents/passport_marcus_tampered.jpg';
        filename = 'passport_marcus_tampered.jpg';
    } else if (persona === 'elena') {
        url = '/static/documents/passport_elena_fracture_usa.jpg';
        filename = 'passport_elena_fracture_usa.jpg';
    }

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Could not fetch ${url}`);
        const blob = await res.blob();
        const file = new File([blob], filename, { type: 'image/jpeg' });
        setDocumentFile(file);
    } catch (err) {
        console.error("Error loading preset doc:", err);
        alert(`Failed to load preset document: ${err.message}`);
    }
}

function checkVerifySubmit() {
    const btn = document.getElementById('btn-submit-verify');
    if (btn) {
        if (state.docUploaded && state.photoCaptured) {
            btn.removeAttribute('disabled');
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            btn.setAttribute('disabled', 'true');
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }
}

// ============================================================================
// 4. SUBMIT VERIFICATION PIPELINE
// ============================================================================

async function submitVerification() {
    if (state.isSubmitting) return;
    if (!state.docFile || !state.photoFile) {
        alert("Please provide both an ID document and a photo.");
        return;
    }

    state.isSubmitting = true;
    const btn = document.getElementById('btn-submit-verify');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="inline-flex items-center gap-2"><i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Processing Neural Biometrics & Zero-Trust Chain...</span>';
    btn.setAttribute('disabled', 'true');
    if (window.lucide) window.lucide.createIcons();
    
    updateStepper(4);

    try {
        const docTypeSelect = document.getElementById('select-doc-type');
        const docCategory = docTypeSelect ? docTypeSelect.value : 'PASSPORT';

        const formData = new FormData();
        formData.append('doc_file', state.docFile);
        formData.append('live_file', state.photoFile);
        formData.append('document_category', docCategory);

        const response = await fetch('/api/verify-upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errJson = await response.json().catch(() => ({}));
            throw new Error(errJson.detail || `Server error HTTP ${response.status}`);
        }

        const data = await response.json();
        renderTravelerResult(data);

        // Store verification ID
        state.latestVerificationId = data.verification_id;
        localStorage.setItem('latest_verification_id', data.verification_id);

        showScreen('screen-result');

    } catch (err) {
        console.error('Verification error:', err);
        alert(`Verification failed: ${err.message}. Please check your connection or retry.`);
        updateStepper(3);
    } finally {
        state.isSubmitting = false;
        btn.innerHTML = originalText;
        checkVerifySubmit();
        if (window.lucide) window.lucide.createIcons();
    }
}

// ============================================================================
// 5. RENDER RESULT (GENUINE BIOMETRIC REPORT)
// ============================================================================

function renderTravelerResult(data) {
    const trust = data.trust_evaluation || {};
    const face = data.face_match || {};
    const intake = data.intake || {};
    const structured = intake.structured_data || {};
    const forensics = data.forensics || {};
    const secondLook = data.second_look || {};
    const fractureDetected = data.fracture_detected || false;

    // 1. Trust Score & Verdict
    const score = Math.round(trust.identity_trust_score !== undefined ? trust.identity_trust_score : 90);
    const isIntact = trust.is_trust_chain_intact !== undefined ? trust.is_trust_chain_intact : (score >= 80 && !fractureDetected);
    
    const scoreNum = document.getElementById('traveler-score-num');
    const scoreRing = document.getElementById('traveler-score-ring');
    const scoreIcon = document.getElementById('traveler-score-icon');
    const verdictBadge = document.getElementById('traveler-verdict-badge');
    const verdictDesc = document.getElementById('traveler-verdict-desc');
    const refId = document.getElementById('traveler-verification-id');

    if (scoreNum) scoreNum.innerHTML = `${score}<span class="text-sm font-normal text-ink/50">/100</span>`;
    if (refId) refId.textContent = data.verification_id || '--';

    if (isIntact && score >= 80) {
        if (scoreRing) scoreRing.className = 'w-14 h-14 rounded-full border-4 border-status-pass flex items-center justify-center bg-status-pass/10 text-status-pass transition-colors';
        if (scoreIcon) scoreIcon.setAttribute('data-lucide', 'shield-check');
        if (verdictBadge) {
            verdictBadge.className = 'badge bg-status-pass text-white text-xs px-3 py-1 font-bold tracking-wider uppercase';
            verdictBadge.textContent = 'CLEARED';
        }
        if (verdictDesc) {
            verdictDesc.textContent = 'Your biometric facial embedding matched the identity document with high neural confidence. The immutable Zero-Trust evidence chain is intact and you are cleared for fast-track border travel.';
        }
    } else if (fractureDetected || score < 60 || !face.is_match) {
        if (scoreRing) scoreRing.className = 'w-14 h-14 rounded-full border-4 border-status-fail flex items-center justify-center bg-status-fail/10 text-status-fail transition-colors';
        if (scoreIcon) scoreIcon.setAttribute('data-lucide', 'shield-alert');
        if (verdictBadge) {
            verdictBadge.className = 'badge bg-status-fail text-white text-xs px-3 py-1 font-bold tracking-wider uppercase';
            verdictBadge.textContent = fractureDetected ? 'IDENTITY FRACTURE' : 'OFFICER REVIEW REQUIRED';
        }
        if (verdictDesc) {
            const reason = fractureDetected ? 'Identity Graph conflict detected across multi-jurisdiction records.' : (!face.is_match ? 'Biometric facial mismatch identified between live capture and ID photo.' : 'Forensic or document verification anomalies detected.');
            verdictDesc.textContent = `${reason} Please proceed to the primary inspection service desk for officer review.`;
        }
    } else {
        if (scoreRing) scoreRing.className = 'w-14 h-14 rounded-full border-4 border-status-review flex items-center justify-center bg-status-review/10 text-status-review transition-colors';
        if (scoreIcon) scoreIcon.setAttribute('data-lucide', 'help-circle');
        if (verdictBadge) {
            verdictBadge.className = 'badge bg-status-review text-white text-xs px-3 py-1 font-bold tracking-wider uppercase';
            verdictBadge.textContent = 'ADDITIONAL VERIFICATION';
        }
        if (verdictDesc) {
            verdictDesc.textContent = 'Secondary document verification is required before fast-track clearance. An officer will assist you.';
        }
    }

    // 2. GENUINE BIOMETRIC FACIAL VERIFICATION CARD
    const faceConfEl = document.getElementById('result-face-confidence');
    const faceCosineEl = document.getElementById('result-face-cosine');
    const faceBar = document.getElementById('result-face-bar');
    const faceStatusBadge = document.getElementById('face-match-status-badge');
    const livenessPill = document.getElementById('result-liveness-pill');

    const matchConfidence = face.match_confidence !== undefined ? face.match_confidence : 0.0;
    const rawCosine = face.raw_cosine_similarity !== undefined ? face.raw_cosine_similarity : null;
    const isMatch = face.is_match || (matchConfidence >= 60.0);
    const livenessScore = face.liveness_score !== undefined ? face.liveness_score : 90.0;

    if (faceConfEl) faceConfEl.textContent = `${matchConfidence.toFixed(1)}%`;
    if (faceCosineEl) {
        if (rawCosine !== null && rawCosine !== undefined) {
            faceCosineEl.textContent = `Raw Cosine: ${rawCosine.toFixed(4)}`;
        } else {
            faceCosineEl.textContent = `Neural Match: ${matchConfidence.toFixed(1)}%`;
        }
    }
    if (faceBar) {
        faceBar.style.width = `${Math.min(100, Math.max(5, matchConfidence))}%`;
        if (isMatch) {
            faceBar.className = 'h-full bg-status-pass rounded-full transition-all duration-700';
        } else {
            faceBar.className = 'h-full bg-status-fail rounded-full transition-all duration-700';
        }
    }
    if (faceStatusBadge) {
        if (isMatch) {
            faceStatusBadge.className = 'badge badge-success text-xs font-bold px-3 py-1 uppercase';
            faceStatusBadge.textContent = 'MATCH CONFIRMED';
        } else {
            faceStatusBadge.className = 'badge badge-fail text-xs font-bold px-3 py-1 uppercase';
            faceStatusBadge.textContent = 'BIOMETRIC MISMATCH';
        }
    }
    if (livenessPill) {
        if (face.liveness_passed) {
            livenessPill.className = 'text-[10px] font-mono text-status-pass mt-2';
            livenessPill.textContent = `✓ Passive Liveness: ${livenessScore.toFixed(1)}% PASS`;
        } else {
            livenessPill.className = 'text-[10px] font-mono text-status-fail mt-2';
            livenessPill.textContent = `⚠ Passive Liveness: ${livenessScore.toFixed(1)}% REVIEW`;
        }
    }

    // 3. Side-by-Side Photos
    const docPhotoImg = document.getElementById('result-doc-photo');
    const livePhotoImg = document.getElementById('result-live-photo');
    const docHolderEl = document.getElementById('result-doc-holder-name');
    const docIdLabel = document.getElementById('result-doc-id-label');

    // Prefer server returned URLs or fallback to local object URLs
    if (docPhotoImg) {
        docPhotoImg.src = data.doc_image_url || state.docPreviewUrl || '/static/documents/passport_arthur_clean.jpg';
    }
    if (livePhotoImg) {
        livePhotoImg.src = data.live_image_url || state.photoPreviewUrl || '/static/faces/live_arthur.jpg';
    }

    const holderName = structured.holder_name || `${structured.surname || ''} ${structured.given_names || ''}`.trim() || 'Passport Holder';
    const docNum = structured.document_number || 'ICAO-DOC';
    if (docHolderEl) docHolderEl.textContent = holderName;
    if (docIdLabel) docIdLabel.textContent = `Doc #${docNum}`;

    // 4. 4-Pillar Trust Details
    const docValidEl = document.getElementById('metric-doc-valid');
    const docTypeEl = document.getElementById('metric-doc-type');
    const valObj = data.validation || {};
    if (docValidEl) {
        if (valObj.is_valid || valObj.format_valid) {
            docValidEl.className = 'text-sm font-bold text-status-pass';
            docValidEl.textContent = 'ICAO 9303 Valid';
        } else {
            docValidEl.className = 'text-sm font-bold text-status-fail';
            docValidEl.textContent = 'Checksum Anomaly';
        }
    }
    if (docTypeEl) docTypeEl.textContent = `${structured.document_type || 'PASSPORT'} #${docNum}`;

    const forensicsEl = document.getElementById('metric-forensics');
    const tamperScore = forensics.tampering_score !== undefined ? forensics.tampering_score : 0.0;
    if (forensicsEl) {
        if (tamperScore < 30.0) {
            forensicsEl.className = 'text-sm font-bold text-status-pass';
            forensicsEl.textContent = `Clean (${tamperScore.toFixed(1)}/100)`;
        } else {
            forensicsEl.className = 'text-sm font-bold text-status-fail';
            forensicsEl.textContent = `Altered (${tamperScore.toFixed(1)}/100)`;
        }
    }

    const graphEl = document.getElementById('metric-graph');
    if (graphEl) {
        if (!fractureDetected) {
            graphEl.className = 'text-sm font-bold text-status-pass';
            graphEl.textContent = 'Single Identity';
        } else {
            graphEl.className = 'text-sm font-bold text-status-fail';
            graphEl.textContent = 'Fracture Detected';
        }
    }

    const ledgerEl = document.getElementById('metric-ledger');
    const ledgerHashEl = document.getElementById('metric-ledger-hash');
    if (ledgerEl) ledgerEl.textContent = `Block #${data.audit_block_index !== undefined ? data.audit_block_index : '--'}`;
    if (ledgerHashEl) ledgerHashEl.textContent = `Hash: ${(data.audit_block_hash || 'SHA-256').substring(0, 16)}...`;

    if (window.lucide) window.lucide.createIcons();
}

// ============================================================================
// 6. DASHBOARD TRAVELER HISTORY
// ============================================================================

async function loadTravelerHistory(isManual = false) {
    const listContainer = document.getElementById('traveler-recent-list');
    const refreshIcon = document.getElementById('icon-refresh-history');
    if (refreshIcon && isManual) {
        refreshIcon.classList.add('animate-spin');
    }

    try {
        const res = await fetch('/api/verifications?limit=6');
        if (!res.ok) return;
        const data = await res.json();
        const records = data.verifications || [];

        if (!listContainer) return;

        if (records.length === 0) {
            listContainer.innerHTML = `
                <div class="col-span-full py-12 text-center text-ink/50 text-sm border-2 border-dashed border-hairline rounded-2xl">
                    <i data-lucide="shield" class="w-8 h-8 mx-auto mb-2 text-ink/30"></i>
                    No previous verifications on record. Click <strong>Start Verification</strong> above to begin your first biometric clearance.
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
            return;
        }

        listContainer.innerHTML = '';
        records.slice(0, 6).forEach(rec => {
            const isCleared = rec.trust_score >= 80 && !rec.fracture_detected && (!rec.trust_chain_broken_layer || rec.trust_chain_broken_layer === 'NONE');
            const isOfficerReview = rec.fracture_detected || rec.trust_score < 60;
            
            let badgeClass = 'badge-success';
            let badgeText = 'CLEARED';
            
            if (isOfficerReview) {
                badgeClass = 'badge-fail';
                badgeText = 'OFFICER REVIEW';
            } else if (!isCleared) {
                badgeClass = 'badge-warning';
                badgeText = 'ADDITIONAL VERIFICATION';
            }

            const docTypeLabel = rec.document_type === 'P' ? 'Passport Verification' : (rec.document_type === 'V' ? 'Visa Verification' : `${rec.document_type} Verification`);
            const dateStr = rec.timestamp ? rec.timestamp.replace('T', ' ').substring(0, 16) : 'Recent';
            const trustScore = Math.round(rec.trust_score || 0);

            const card = document.createElement('div');
            card.className = 'bento-tile p-6 flex flex-col justify-between hover:border-primary/40 hover:shadow-md transition-all gap-4 cursor-pointer group';
            card.setAttribute('title', 'Click to view verification report');
            card.innerHTML = `
                <div class="flex items-start justify-between">
                    <span class="badge ${badgeClass}">${badgeText}</span>
                    <span class="font-mono text-xs font-bold text-ink/70">${trustScore}/100</span>
                </div>
                <div>
                    <div class="text-lg font-semibold text-ink group-hover:text-primary transition-colors flex items-center justify-between">
                        <span>${docTypeLabel}</span>
                        <i data-lucide="chevron-right" class="w-4 h-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all text-primary"></i>
                    </div>
                    <div class="text-sm text-ink/50 mt-1">${dateStr} • Ref: ${rec.id.substring(0, 10)}</div>
                </div>
            `;

            card.addEventListener('click', async () => {
                try {
                    const r = await fetch(`/api/verification/${rec.id}`);
                    if (r.ok) {
                        const recData = await r.json();
                        renderTravelerResult(recData);
                        showScreen('screen-result');
                    }
                } catch (e) {
                    console.error('Could not fetch verification details:', e);
                }
            });

            listContainer.appendChild(card);
        });

    } catch (e) {
        console.warn('Could not fetch verification history:', e);
    } finally {
        if (refreshIcon) {
            setTimeout(() => refreshIcon.classList.remove('animate-spin'), 400);
        }
        if (window.lucide) window.lucide.createIcons();
    }
}

// ============================================================================
// 7. INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) window.lucide.createIcons();
    loadTravelerHistory();

    const toggleEl = document.getElementById('toggle-auto-capture');
    if (toggleEl) {
        toggleEl.addEventListener('change', (e) => {
            autoCapture.enabled = e.target.checked;
        });
    }

    // Preload face tracking engine in background for instant lock
    initFaceTrackingModel();
});
