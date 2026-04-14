import gradio as gr
import requests
import json
import time
import shutil
import os
from PIL import Image
from io import BytesIO

COMFYUI_URL = "https://u955219-s8vn-ce8c25bc.westd.seetacloud.com:8443"

def run_workflow(person_image, clothing_image):
    # 保存图像到ComfyUI input文件夹
    input_dir = "/root/autodl-tmp/ComfyUI/input"
    os.makedirs(input_dir, exist_ok=True)
    
    person_path = os.path.join(input_dir, "person.jpg")
    clothing_path = os.path.join(input_dir, "clothing.jpg")
    
    # 保存上传的图像
    person_image.save(person_path)
    clothing_image.save(clothing_path)
    
    # 加载工作流JSON
    workflow_path = "/root/autodl-tmp/ComfyUI/user/default/workflows/云绘基础工作流/Flux图像系列/demo1.json"
    with open(workflow_path, "r", encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 修改LoadImage节点
    # 节点ID: 33 (person), 36 (clothing), 127 (inpaint image)
    for node in workflow["nodes"]:
        if node["id"] == 33:
            node["widgets_values"][0] = "person.jpg"
        elif node["id"] == 36:
            node["widgets_values"][0] = "clothing.jpg"
        elif node["id"] == 127:
            node["widgets_values"][0] = "person.jpg"  # inpaint使用person图像
    
    # 发送工作流到ComfyUI API
    try:
        response = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow}, timeout=10)
        response.raise_for_status()
        prompt_id = response.json()["prompt_id"]
    except requests.exceptions.RequestException as e:
        return f"错误：无法连接到ComfyUI API。请确保ComfyUI正在运行在 {COMFYUI_URL}。错误详情：{str(e)}"
    
    # 轮询工作流状态
    max_attempts = 300  # 最多等待5分钟
    attempts = 0
    while attempts < max_attempts:
        try:
            history_response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            history_response.raise_for_status()
            history = history_response.json()
            
            if prompt_id in history:
                status = history[prompt_id]["status"]
                if status["completed"]:
                    break
                elif status["status_str"] == "error":
                    return f"工作流执行出错：{status.get('messages', '未知错误')}"
            
            time.sleep(1)
            attempts += 1
        except requests.exceptions.RequestException:
            return "错误：检查工作流状态时网络错误。"
    
    if attempts >= max_attempts:
        return "错误：工作流执行超时。"
    
    # 获取输出图像（节点126的PreviewImage）
    try:
        output = history[prompt_id]["outputs"]
        if "126" not in output or "images" not in output["126"]:
            return "错误：未找到输出图像。"
        
        image_data = output["126"]["images"][0]
        image_url = f"{COMFYUI_URL}/view?filename={image_data['filename']}&subfolder={image_data.get('subfolder', '')}&type={image_data.get('type', 'output')}"
        
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        
        img = Image.open(BytesIO(image_response.content))
        return img
    except Exception as e:
        return f"错误：获取输出图像失败。{str(e)}"

# 创建Gradio界面
iface = gr.Interface(
    fn=run_workflow,
    inputs=[
        gr.Image(label="用户图像", type="pil"),
        gr.Image(label="衣物图像", type="pil")
    ],
    outputs=gr.Image(label="生成结果"),
    title="虚拟试衣系统",
    description="上传用户全身图像和衣物图像，系统将使用CatVTON和Flux2生成试衣效果。请确保ComfyUI正在后台运行。"
)

if __name__ == "__main__":
    print("启动虚拟试衣Gradio应用...")
    print("请确保ComfyUI已启动：cd /root/autodl-tmp/ComfyUI && python main.py --enable-cors-header --listen 0.0.0.0 --port 8188")
    iface.launch(server_name="0.0.0.0", server_port=7860)