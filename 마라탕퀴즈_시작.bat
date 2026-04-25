@echo off
chcp 65001 > nul
title 마라탕퀴즈 서버

REM 항상 이 .bat 파일이 있는 폴더로 이동
cd /d "%~dp0"

echo.
echo ============================================
echo   마라탕 퀴즈 서버 시작 중...
echo ============================================
echo.
echo 작업 폴더: %CD%
echo.

REM Python 위치 확인
where python > nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python을 찾을 수 없습니다. PATH 등록 필요.
  pause
  exit /b 1
)

REM Flask 서버 백그라운드 시작
start "마라탕퀴즈 서버" /MIN python scripts\05_serve.py

REM 서버 부팅 대기 (3초)
echo 서버 부팅 중...
timeout /t 3 /nobreak > nul

REM 기본 브라우저로 자동 열기 (앱 모드)
start "" "http://localhost:8765/"

echo.
echo ✅ 서버 실행 중: http://localhost:8765/
echo.
echo 브라우저 주소창 옆 ⊕ 또는 설치 버튼 누르면 앱처럼 설치 가능
echo (Edge: 우측 상단 ... ^> 앱 ^> 이 사이트를 앱으로 설치)
echo (Chrome: 주소창 우측 ⊕ 아이콘 클릭)
echo.
echo 이 창을 닫으면 서버가 종료됩니다.
echo ============================================
echo.

REM 사용자가 닫을 때까지 대기
pause > nul
