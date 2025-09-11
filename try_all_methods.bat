@echo off
REM Try all available camera access methods

echo ============================================
echo  Camera Access Test Suite
echo ============================================
echo.

echo Testing different camera access methods...
echo.

echo 1. Testing OpenCV camera access:
python -c "import cv2; [print(f'Camera {i}:', cv2.VideoCapture(i, cv2.CAP_DSHOW).isOpened()) for i in range(3)]"
echo.

echo 2. Testing FFmpeg device listing:
python list_ffmpeg_devices.py
echo.

echo 3. Testing OpenCV RTSP server (may work even if FFmpeg doesn't):
start "OpenCV RTSP Test" python opencv_rtsp_server.py --camera 0
timeout /t 3 /nobreak >nul

echo Testing RTSP connection...
python opencv_rtsp_server.py --test-connection rtsp://localhost:8554/live
echo.

echo 4. Testing simple RTSP server (with fallback):
start "Simple RTSP Test" python simple_rtsp_server.py --camera 0
timeout /t 3 /nobreak >nul

echo Testing RTSP connection...
python -c "import cv2; cap = cv2.VideoCapture('rtsp://localhost:8554/live', cv2.CAP_FFMPEG); print('RTSP connection:', cap.isOpened()); cap.release()"
echo.

echo ============================================
echo  Test completed!
echo ============================================
echo.
echo If any method worked, you can use that approach.
echo Check the output above to see which methods succeeded.
echo.
pause
