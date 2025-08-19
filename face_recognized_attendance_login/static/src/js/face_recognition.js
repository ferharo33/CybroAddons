/** @odoo-module **/
import kiosk from "@hr_attendance/public_kiosk/public_kiosk_app";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
const MODEL_URL = '/face_recognized_attendance_login/static/src/js/weights';
faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL)
faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL)
faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
faceapi.nets.tinyFaceDetector.load(MODEL_URL),
faceapi.nets.faceLandmark68TinyNet.load(MODEL_URL),
faceapi.nets.faceExpressionNet.load(MODEL_URL),
faceapi.nets.ageGenderNet.load(MODEL_URL)

patch(kiosk.kioskAttendanceApp.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.employee_image = useRef("employee_image");
        this.video = useRef("video");
        this.notification = useService("notification");
        this.state.employee = false;
        this.state.verifiedEmployeeId = null
        this.isRecognitionActive = false;
        this.currentStream = null;
        this.faceMatcher = null;
        this.noMatchCount = 0;
    },

    async loadImage(employeeId) {
        var image = await this.rpc("/get_image", {
            employee_id: employeeId
        })
        this.have_image = image
        const employee_image = this.employee_image.el
        employee_image.src = "data:image/jpeg;base64," + image
        this.currentVerificationId = employeeId;
    },

    async startWebcam() {
        const video = this.video.el;
        if (video) {
            video.srcObject = null;
            video.style.display = 'block';
        }
        this.isRecognitionActive = true;
        this.state.employee = false;
        this.noMatchCount = 0; // Reset no match counter
        this.faceMatcher = null; // Reset faceMatcher

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            this.currentStream = stream;
            video.srcObject = stream;
            await new Promise(resolve => {
                video.onloadedmetadata = resolve;
            });
            await this.faceRecognition(video);
        } catch (error) {
            console.error("Error starting webcam:", error);
            this.isRecognitionActive = false;
            this.notification.add(_t("Your browser does not support camera access. Please try a different browser."), {
                title : "Access Denied !",
                type: "danger",
            });
        }
    },

    async getLabeledFaceDescriptions() {
        const employee_image = this.employee_image.el;
        const detections = await faceapi
            .detectSingleFace(employee_image)
            .withFaceLandmarks()
            .withFaceExpressions()
            .withFaceDescriptor();
        return detections;
    },

    stopRecognition(video, canvas) {
        this.isRecognitionActive = false;
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
        if (video) {
            video.srcObject = null;
            video.style.display = 'none';
        }
        if (canvas && canvas.parentNode) {
            canvas.remove();
        }
        const modal = document.getElementById('WebCamModal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.faceMatcher = null;
        this.noMatchCount = 0;
    },

    async faceRecognition(video) {
        if (!this.isRecognitionActive) return;
        if (!this.faceMatcher) {
            const labeledFaceDescriptors = await this.getLabeledFaceDescriptions();
            if (labeledFaceDescriptors && labeledFaceDescriptors.descriptor) {
                this.faceMatcher = new faceapi.FaceMatcher([labeledFaceDescriptors.descriptor]);
            } else {
                console.error("Could not get face descriptor from reference image");
                this.notification.add(_t("Failed to initialize face recognition, Please upload a new, properly formatted image."), {
                    type: "danger",
                    title: "Image detection failed!",
                });
                this.stopRecognition(video);
                return;
            }
        }
        const canvas = faceapi.createCanvasFromMedia(video);
        document.body.append(canvas);
        canvas.style.display = 'none'
        const displaySize = { width: video.videoWidth, height: video.videoHeight };
        faceapi.matchDimensions(canvas, displaySize);
        const processFrame = async () => {
            if (!this.isRecognitionActive) return;
            try {
                const detections = await faceapi
                    .detectAllFaces(video)
                    .withFaceLandmarks()
                    .withFaceExpressions()
                    .withFaceDescriptors();
                if (detections.length === 0) {
                    if (this.isRecognitionActive) {
                        requestAnimationFrame(processFrame);
                    }
                    return;
                }
                for (const detection of detections) {
                    const match = this.faceMatcher.findBestMatch(detection.descriptor);
                    if (match._distance < 0.4) {
                        this.state.employee = true;
                        this.state.verifiedEmployeeId = this.currentVerificationId;
                        this.stopRecognition(video, canvas);
                        return;
                    } else {
                        this.noMatchCount++;
                        if (this.noMatchCount >= 3) {
                            this.notification.add(_t("Sorry, cannot recognize you"), {
                                title:"Recognition Failed ! ",
                                type: "danger",
                            });
                            this.stopRecognition(video, canvas);
                            return;
                        }
                    }
                }
                if (this.isRecognitionActive) {
                    requestAnimationFrame(processFrame);
                }
            } catch (error) {
                console.error("Face recognition error:", error);
                this.stopRecognition(video, canvas);
            }
        };
        processFrame();
    },

    async onManualSelection(employeeId, enteredPin) {
        if (this.isRecognitionActive) {
            this.stopRecognition(this.video.el);
        }
        await this.loadImage(employeeId);
        if (this.have_image) {
            const modal = document.getElementById('WebCamModal');
            if (modal) {
                modal.style.display = 'block';
            }
            await this.startWebcam();
            const checkInterval = setInterval(() => {
                if (this.state.employee && this.state.verifiedEmployeeId === employeeId) {
                    clearInterval(checkInterval);
                    this.rpc("manual_selection", {
                        token: this.props.token,
                        employee_id: employeeId,
                        pin_code: enteredPin,
                    }).then(result => {
                        if (result && result.attendance) {
                            this.employeeData = result;
                            this.switchDisplay("greet");
                        } else {
                            if (enteredPin) {
                                this.notification.add(_t("Wrong Pin"), {
                                    type: "danger",
                                });
                            }
                        }
                    });
                }
            }, 500);
        } else {
            await this.popup.add(ErrorPopup, {
                title: _t("Authentication failed"),
                body: _t("Selected cashier has no image."),
            });
            location.reload();
        }
    },
});