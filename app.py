import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from util import generate_subtasks, extract_text_from_pdf, generate_title, data_with_visualization, get_knowledge

app = Flask(__name__)
CORS(app)

# 确保uploads目录存在
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def hello():
    return 'Backend listening...'


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    question = request.form.get('question')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    if file and file.filename.endswith('.pdf'):
        try:
            # 保存文件
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            
            # 生成标题
            title = generate_title(question)
            
            # 获取知识数据
            knowledge_data = get_knowledge(file_path, question)
            
            # 添加可视化信息
            result = data_with_visualization(knowledge_data)
            
            # 返回成功响应和完整分析结果
            return jsonify({
                'message': 'File uploaded and analyzed successfully',
                'filename': file.filename,
                'question': question,
                'title': title,
                'knowledge_data': result
            })
        except Exception as e:
            return jsonify({
                'error': 'Error processing file',
                'details': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9027, debug=True)