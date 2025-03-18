"""
Web Interface Module
Provides web-based monitoring and control interface using Flask
"""

from flask import Flask, render_template, jsonify, request
import logging
from typing import Any
import threading
import time
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)
system = None  # Will be set when server starts

@app.route('/')
def index():
    """Render main monitoring page"""
    return render_template('index.html')

@app.route('/get_status')
def get_status():
    """Get current system status"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        return jsonify({
            'is_running': system.is_running,
            'is_sterilizing': system.is_sterilizing,
            'current_operation': system.current_operation
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/trigger_analysis', methods=['POST'])
def trigger_analysis():
    """Trigger cell analysis"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        image = system.cell_analyzer.capture_image()
        results = system.cell_analyzer.analyze_image(image)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/dispense', methods=['POST'])
def dispense_liquid():
    """Trigger liquid dispensing"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        data = request.get_json()
        volume = data.get('volume', 0)
        pump_id = data.get('pump_id', 1)
        
        command = {
            'type': 'dispense_liquid',
            'params': {
                'volume': volume,
                'pump_id': pump_id
            }
        }
        
        system.command_queue.put(command)
        return jsonify({'status': 'Command queued'})
        
    except Exception as e:
        logger.error(f"Error in dispense: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/move', methods=['POST'])
def move_robot():
    """Control robot arm movement"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        data = request.get_json()
        command = {
            'type': 'move_robot',
            'params': {
                'x': data.get('x', 0),
                'y': data.get('y', 0),
                'z': data.get('z', 0),
                'speed': data.get('speed', 50)
            }
        }
        
        system.command_queue.put(command)
        return jsonify({'status': 'Command queued'})
        
    except Exception as e:
        logger.error(f"Error in move: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/start_sterilization', methods=['POST'])
def start_sterilization():
    """Start sterilization routine"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        command = {
            'type': 'sterilize',
            'params': {
                'duration': 300  # 기본값 5분
            }
        }
        
        system.command_queue.put(command)
        return jsonify({'status': 'Sterilization started'})
        
    except Exception as e:
        logger.error(f"Error in sterilization: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    """Trigger emergency stop"""
    try:
        if system is None:
            return jsonify({'error': 'System not initialized'}), 500
            
        system.emergency_stop()
        return jsonify({'status': 'Emergency stop triggered'})
        
    except Exception as e:
        logger.error(f"Error in emergency stop: {str(e)}")
        return jsonify({'error': str(e)}), 500

def start_web_server(system):
    """Start Flask web server"""
    global app
    app.system = system
    
    # 필요한 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # HTML 템플릿 생성
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>세포 배양 자동화 시스템</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>세포 배양 자동화 시스템</h1>
        
        <div class="card mb-4">
            <div class="card-header">
                시스템 상태
            </div>
            <div class="card-body">
                <p>시스템 상태: <span id="system-status">확인 중...</span></p>
                <p>현재 작업: <span id="current-operation">확인 중...</span></p>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header">
                        세포 분석
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="triggerAnalysis()">분석 시작</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header">
                        살균
                    </div>
                    <div class="card-body">
                        <button class="btn btn-warning" onclick="startSterilization()">살균 시작</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header">
                        비상 정지
                    </div>
                    <div class="card-body">
                        <button class="btn btn-danger" onclick="emergencyStop()">비상 정지</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/get_status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('system-status').textContent = 
                        data.is_running ? '실행 중' : '정지됨';
                    document.getElementById('current-operation').textContent = 
                        data.current_operation || '대기 중';
                })
                .catch(error => console.error('Error:', error));
        }

        function triggerAnalysis() {
            fetch('/trigger_analysis', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert('분석이 시작되었습니다.');
                })
                .catch(error => console.error('Error:', error));
        }

        function startSterilization() {
            fetch('/start_sterilization', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert('살균이 시작되었습니다.');
                })
                .catch(error => console.error('Error:', error));
        }

        function emergencyStop() {
            if (confirm('정말 비상 정지를 실행하시겠습니까?')) {
                fetch('/emergency_stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('비상 정지가 실행되었습니다.');
                    })
                    .catch(error => console.error('Error:', error));
            }
        }

        // 상태 업데이트 주기 설정
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
        ''')
    
    # Flask 서버 실행 (모든 IP에서 접속 가능하도록 설정)
    app.run(host='0.0.0.0', port=8080, debug=True) 