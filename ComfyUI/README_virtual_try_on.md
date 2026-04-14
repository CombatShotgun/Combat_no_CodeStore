# 虚拟试衣系统

这是一个基于Gradio的前端界面，用于虚拟试衣项目。系统集成了CatVTON（用于服装替换）和Flux2（用于人物姿势与背景重绘）。

## 功能特点

- 上传用户全身图像和衣物图像
- 自动生成服装试穿效果
- 使用先进的AI模型进行图像处理

## 使用步骤

1. **启动ComfyUI服务器**：
   ```bash
   cd /root/autodl-tmp/ComfyUI
   python main.py --enable-cors-header --listen 0.0.0.0 --port 8188
   ```

2. **启动Gradio前端**：
   ```bash
   cd /root/autodl-tmp/ComfyUI
   python virtual_try_on.py
   ```

3. **访问界面**：
   打开浏览器访问 `http://localhost:7860`

4. **使用界面**：
   - 上传用户全身图像（建议包含完整人物）
   - 上传衣物图像（服装图片）
   - 点击"提交"按钮
   - 等待处理完成，查看生成结果

## 技术栈

- **前端**：Gradio
- **后端**：ComfyUI API
- **AI模型**：
  - CatVTON：服装虚拟试穿
  - Flux2：图像重绘和姿势调整
  - SegformerB2：服装分割遮罩生成

## 注意事项

- 确保ComfyUI服务器正在运行
- 上传的图像应为JPG格式
- 处理时间可能需要几分钟，取决于硬件性能
- 建议使用高清图像以获得更好效果

## 工作流说明

系统使用预定义的ComfyUI工作流，包括：
- 图像加载和预处理
- 服装遮罩生成
- CatVTON服装替换
- Flux2图像重绘
- 最终结果输出