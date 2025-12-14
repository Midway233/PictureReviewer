import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ExifTags
import os
import glob
import datetime

class PictureReviewer:
    def __init__(self, root):
        self.root = root
        self.root.title("图片浏览分类器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 初始化变量
        self.image_folder = ""
        self.image_list = []
        self.current_index = 0
        self.save_list = []
        self.current_image_path = ""
        
        # 设置主题样式
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Save.TButton', background='green', foreground='white')
        style.map('Save.TButton', background=[('active', '#008800')])
        style.configure('Delete.TButton', background='red', foreground='white')
        style.map('Delete.TButton', background=[('active', '#cc0000')])
        
        # 创建界面组件
        self.create_widgets()
        
    def create_widgets(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择文件夹", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 列表菜单
        list_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="列表", menu=list_menu)
        list_menu.add_command(label="查看保存列表", command=lambda: self.show_list_dialog("save"))
        list_menu.add_command(label="载入保存列表", command=self.load_save_list)
        list_menu.add_command(label="移动保存列表图片", command=self.move_saved_images)
        
        # 导出菜单
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="导出", menu=export_menu)
        export_menu.add_command(label="导出保存列表", command=self.export_save_list)
        
        # 主内容区域
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧边栏 - EXIF信息和操作按钮
        self.left_frame = tk.Frame(self.main_frame, width=250, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.left_frame.pack_propagate(False)
        
        # EXIF信息标题
        self.exif_title = tk.Label(self.left_frame, text="EXIF信息", font=('Arial', 11, 'bold'), 
                                 bg="#f0f0f0", fg="#333333")
        self.exif_title.pack(fill=tk.X, padx=10, pady=10)
        
        # EXIF信息文本
        self.exif_text = tk.Label(self.left_frame, text="", justify=tk.LEFT, 
                                 font=('Arial', 9), bg="#f0f0f0", fg="#666666",
                                 wraplength=230)
        self.exif_text.pack(fill=tk.X, padx=10, pady=5)
        
        # 操作按钮区域
        self.action_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 导航按钮
        self.nav_frame = tk.Frame(self.action_frame, bg="#f0f0f0")
        self.nav_frame.pack(fill=tk.X, pady=5)
        
        self.prev_button = ttk.Button(self.nav_frame, text="上一张", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.next_button = ttk.Button(self.nav_frame, text="下一张", command=self.next_image)
        self.next_button.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # 分类按钮
        self.cat_frame = tk.Frame(self.action_frame, bg="#f0f0f0")
        self.cat_frame.pack(fill=tk.X, pady=10)
        
        self.save_button = ttk.Button(self.cat_frame, text="保存 (Y)", 
                                     style='Save.TButton', command=self.save_image)
        self.save_button.pack(fill=tk.X, pady=5)
        
        self.next_button_key = ttk.Button(self.cat_frame, text="下一张 (N)", 
                                       style='Delete.TButton', command=self.next_image)
        self.next_button_key.pack(fill=tk.X, pady=5)
        
        # 列表按钮
        self.list_frame = tk.Frame(self.action_frame, bg="#f0f0f0")
        self.list_frame.pack(fill=tk.X, pady=10)
        
        self.view_save_button = tk.Button(self.list_frame, text="查看保存列表", 
                                        bg="#4CAF50", fg="white", command=lambda: self.show_list_dialog("save"))
        self.view_save_button.pack(fill=tk.X, pady=5)
        
        # 导出按钮
        self.export_frame = tk.Frame(self.action_frame, bg="#f0f0f0")
        self.export_frame.pack(fill=tk.X, pady=10)
        
        self.export_save_button = ttk.Button(self.export_frame, text="导出保存列表", 
                                           command=self.export_save_list)
        self.export_save_button.pack(fill=tk.X, pady=5)
        
        # 右侧区域 - 图片显示和控制
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 顶部信息栏
        self.info_frame = tk.Frame(self.right_frame)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        # 文件信息标签
        self.file_info_label = tk.Label(self.info_frame, text="", justify=tk.LEFT, 
                                       font=('Arial', 10), fg="#333333")
        self.file_info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 列表统计标签
        self.list_info_label = tk.Label(self.info_frame, text="", justify=tk.RIGHT, 
                                      font=('Arial', 10), fg="blue")
        self.list_info_label.pack(side=tk.RIGHT)
        
        # 图片显示区域
        self.image_frame = tk.Frame(self.right_frame, bg="#222222", relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.image_label = tk.Label(self.image_frame, bg="#222222")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="请先选择文件夹", bd=1, relief=tk.SUNKEN, 
                                   anchor=tk.W, font=('Arial', 9))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定键盘快捷键
        self.root.bind('<a>', lambda event: self.prev_image())
        self.root.bind('<A>', lambda event: self.prev_image())
        self.root.bind('<Left>', lambda event: self.prev_image())
        self.root.bind('<d>', lambda event: self.next_image())
        self.root.bind('<D>', lambda event: self.next_image())
        self.root.bind('<Right>', lambda event: self.next_image())
        self.root.bind('<y>', lambda event: self.save_image())
        self.root.bind('<Y>', lambda event: self.save_image())
        self.root.bind('<n>', lambda event: self.next_image())
        self.root.bind('<N>', lambda event: self.next_image())
        
        # 绑定窗口大小变化事件
        self.image_frame.bind('<Configure>', lambda event: self.resize_and_display_image())
    
    def select_folder(self):
        # 选择文件夹
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            # 获取所有JPEG图片 - 使用集合去重
            image_files = set()
            # 遍历所有支持的扩展名（包括大小写）
            for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
                files = glob.glob(os.path.join(self.image_folder, ext))
                image_files.update(files)
            # 转换回列表并排序
            self.image_list = sorted(list(image_files))
            
            if not self.image_list:
                messagebox.showinfo("提示", "该文件夹中没有JPEG图片")
                return
            
            # 初始化列表
            self.current_index = 0
            self.save_list = []
            
            # 显示第一张图片
            self.show_current_image()
            self.update_status()
    
    def show_current_image(self):
        if 0 <= self.current_index < len(self.image_list):
            self.current_image_path = self.image_list[self.current_index]
            
            # 打开并调整图片大小 - 自适应窗口大小
            self.resize_and_display_image()
            
            # 显示EXIF信息
            self.show_exif_info()
            
            # 更新信息显示
            self.update_info_display()
            self.update_status()
        elif self.current_index >= len(self.image_list):
            # 所有图片已显示完毕
            if messagebox.askyesno("提示", "所有图片已遍历完成，是否重新开始？"):
                self.current_index = 0
                self.show_current_image()
            else:
                self.image_label.config(image="")
                self.update_info_display()
                self.update_status()
                self.exif_text.config(text="")
    
    def save_image(self):
        if self.current_image_path:
            # 将图片名称添加到保存列表
            image_name = os.path.basename(self.current_image_path)
            if image_name not in self.save_list:
                self.save_list.append(image_name)
            
            # 显示下一张图片
            if self.current_index < len(self.image_list) - 1:
                self.current_index += 1
                self.show_current_image()
            else:
                # 所有图片已显示完毕
                if messagebox.askyesno("提示", "所有图片已遍历完成，是否重新开始？"):
                    self.current_index = 0
                    self.show_current_image()
                else:
                    self.image_label.config(image="")
                    self.update_info_display()
                    self.update_status()
                    self.exif_text.config(text="")
            
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()
            
    def next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_current_image()
        else:
            # 所有图片已显示完毕
            if messagebox.askyesno("提示", "所有图片已遍历完成，是否重新开始？"):
                self.current_index = 0
                self.show_current_image()
            else:
                self.image_label.config(image="")
                self.update_info_display()
                self.update_status()
                self.exif_text.config(text="")
    
    def export_save_list(self):
        if not self.save_list:
            messagebox.showinfo("提示", "保存列表为空")
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="save_list.txt"
        )
        
        if file_path:
            # 保存列表
            with open(file_path, "w", encoding="utf-8") as f:
                for image_name in self.save_list:
                    f.write(image_name + "\n")
            messagebox.showinfo("提示", f"保存列表已导出到：{file_path}")
    
    def load_save_list(self):
        """载入已存在的待保存图片列表"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="选择待保存图片列表文件"
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.save_list = [line.strip() for line in f.readlines() if line.strip()]
                messagebox.showinfo("提示", f"成功载入 {len(self.save_list)} 张图片到保存列表")
                self.update_info_display()
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"载入保存列表时出错：{e}")
    
    def move_saved_images(self):
        """将所有保存列表中的图片移动到子文件夹"""
        if not self.save_list:
            messagebox.showinfo("提示", "保存列表为空，无法移动图片")
            return
        
        if not self.image_folder:
            messagebox.showinfo("提示", "请先选择图片文件夹")
            return
        
        # 创建目标文件夹
        saved_folder = os.path.join(self.image_folder, "已保存图片")
        if not os.path.exists(saved_folder):
            try:
                os.makedirs(saved_folder)
            except Exception as e:
                messagebox.showerror("错误", f"创建文件夹时出错：{e}")
                return
        
        # 移动图片
        moved_count = 0
        failed_count = 0
        
        for image_name in self.save_list:
            src_path = os.path.join(self.image_folder, image_name)
            dst_path = os.path.join(saved_folder, image_name)
            
            if os.path.exists(src_path):
                try:
                    os.rename(src_path, dst_path)
                    moved_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"移动 {image_name} 失败：{e}")
            else:
                failed_count += 1
        
        # 更新保存列表（只保留成功移动的图片）
        self.save_list = [image_name for image_name in self.save_list 
                        if not os.path.exists(os.path.join(self.image_folder, image_name))]
        
        messagebox.showinfo("提示", f"移动完成！成功移动 {moved_count} 张图片，失败 {failed_count} 张图片")
        self.update_info_display()
        self.update_status()
    
    def show_exif_info(self):
        try:
            image = Image.open(self.current_image_path)
            exif_data = image._getexif()
            if exif_data:
                exif_info = {}
                for tag, value in exif_data.items():
                    if tag in ExifTags.TAGS:
                        tag_name = ExifTags.TAGS[tag]
                        if tag_name in ['DateTimeOriginal', 'DateTime', 'Make', 'Model', 'FocalLength', 'FocalLengthIn35mmFilm', 'FNumber', 'ExposureTime', 'ISO', 'LensModel']:
                            if isinstance(value, bytes):
                                # 尝试多种编码方式解码镜头型号
                                try:
                                    value = value.decode('utf-8', errors='replace')
                                except:
                                    try:
                                        value = value.decode('ascii', errors='replace')
                                    except:
                                        value = value.hex()  # 如果所有编码都失败，显示十六进制
                                # 过滤掉不可打印字符
                                value = ''.join(c for c in value if c.isprintable() or c in '\t\n\r')
                                # 清除字符串两端的空白字符
                                value = value.strip()
                            elif isinstance(value, tuple) and len(value) == 2:
                                # 处理分数格式的数值（如焦距）
                                value = f"{value[0]}/{value[1]}" if value[1] != 0 else str(value[0])
                            elif tag_name == 'ISO':
                                # 特殊处理ISO值
                                if isinstance(value, int):
                                    # 直接使用整数值
                                    pass
                                elif isinstance(value, tuple):
                                    # 有些相机可能返回ISO范围，取第一个值
                                    value = str(value[0]) if value else 'Unknown'
                                else:
                                    # 其他情况尝试转换为字符串
                                    value = str(value)
                            exif_info[tag_name] = value
                
                # 格式化显示EXIF信息 - 垂直排列
                display_lines = []
                if 'DateTimeOriginal' in exif_info:
                    display_lines.append(f"拍摄时间：{exif_info['DateTimeOriginal']}")
                if 'Make' in exif_info:
                    display_lines.append(f"相机品牌：{exif_info['Make']}")
                if 'Model' in exif_info:
                    display_lines.append(f"相机型号：{exif_info['Model']}")
                if 'FocalLength' in exif_info:
                    display_lines.append(f"焦距：{exif_info['FocalLength']}mm")
                if 'FocalLengthIn35mmFilm' in exif_info:
                    display_lines.append(f"35mm等效焦距：{exif_info['FocalLengthIn35mmFilm']}mm")
                if 'LensModel' in exif_info:
                    display_lines.append(f"镜头型号：{exif_info['LensModel']}")
                if 'FNumber' in exif_info:
                    display_lines.append(f"光圈：f/{exif_info['FNumber']}")
                if 'ExposureTime' in exif_info:
                    display_lines.append(f"快门：{exif_info['ExposureTime']}s")
                if 'ISO' in exif_info:
                    display_lines.append(f"ISO：{exif_info['ISO']}")
                
                if display_lines:
                    self.exif_text.config(text="\n".join(display_lines))
                else:
                    self.exif_text.config(text="无关键EXIF信息")
            else:
                self.exif_text.config(text="无EXIF信息")
        except Exception as e:
            self.exif_text.config(text="无法读取EXIF信息")
    
    def resize_and_display_image(self):
        """根据窗口大小自适应调整图片显示"""
        if not self.current_image_path:
            return
        
        image = Image.open(self.current_image_path)
        
        # 获取当前图片显示区域的大小
        img_width = self.image_frame.winfo_width() - 20  # 减去边距
        img_height = self.image_frame.winfo_height() - 20  # 减去边距
        
        if img_width <= 0 or img_height <= 0:
            # 如果窗口还没初始化完成，使用默认大小
            img_width = 600
            img_height = 400
        
        # 计算缩放比例
        img_ratio = image.width / image.height
        frame_ratio = img_width / img_height
        
        if img_ratio > frame_ratio:
            # 图片更宽，以宽度为基准缩放
            new_width = img_width
            new_height = int(img_width / img_ratio)
        else:
            # 图片更高，以高度为基准缩放
            new_height = img_height
            new_width = int(img_height * img_ratio)
        
        # 调整图片大小
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        # 显示图片
        self.image_label.config(image=photo)
        self.image_label.image = photo
    
    def show_list_dialog(self, list_type):
        """显示保存列表的对话框"""
        title = "保存列表"
        image_list = self.save_list
        bg_color = "#4CAF50"
        text_color = "white"
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置对话框样式
        dialog.configure(bg="#f0f0f0")
        
        # 创建列表框架
        list_frame = tk.Frame(dialog, bg="white", relief=tk.SUNKEN, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建列表控件
        self.listbox = tk.Listbox(list_frame, font=('Arial', 10), selectmode=tk.SINGLE, 
                                bg="white", fg="#333333", bd=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # 缩略图显示区域
        thumb_frame = tk.Frame(dialog, width=200, bg="#e0e0e0", relief=tk.SUNKEN, bd=1)
        thumb_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=10)
        thumb_frame.pack_propagate(False)
        
        # 缩略图显示
        self.thumb_label = tk.Label(thumb_frame, bg="#e0e0e0")
        self.thumb_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 操作按钮
        button_frame = tk.Frame(dialog, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 关闭按钮
        close_button = tk.Button(button_frame, text="关闭", width=15, 
                                bg="#607d8b", fg="white", command=dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # 填充列表
        for image_name in image_list:
            self.listbox.insert(tk.END, image_name)
        
        # 绑定列表选择事件
        self.listbox.bind('<<ListboxSelect>>', lambda event: self.show_thumbnail(image_list, dialog))
        
        # 设置当前列表类型
        self.current_list_dialog = dialog
        self.current_list_type = list_type
    
    def show_thumbnail(self, image_list, dialog):
        """显示选中图片的缩略图"""
        try:
            selection = self.listbox.curselection()
            if selection:
                index = selection[0]
                if index < len(image_list):
                    image_name = image_list[index]
                    image_path = os.path.join(self.image_folder, image_name)
                    
                    # 打开图片
                    image = Image.open(image_path)
                    
                    # 获取缩略图区域的大小
                    thumb_width = self.thumb_label.winfo_width() - 20  # 减去边距
                    thumb_height = self.thumb_label.winfo_height() - 20  # 减去边距
                    
                    if thumb_width <= 0 or thumb_height <= 0:
                        # 如果窗口还没初始化完成，使用默认大小
                        thumb_width = 180
                        thumb_height = 150
                    
                    # 计算缩放比例
                    img_ratio = image.width / image.height
                    frame_ratio = thumb_width / thumb_height
                    
                    if img_ratio > frame_ratio:
                        # 图片更宽，以宽度为基准缩放
                        new_width = thumb_width
                        new_height = int(thumb_width / img_ratio)
                    else:
                        # 图片更高，以高度为基准缩放
                        new_height = thumb_height
                        new_width = int(thumb_height * img_ratio)
                    
                    # 调整图片大小
                    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # 显示缩略图
                    self.thumb_label.config(image=photo)
                    self.thumb_label.image = photo
        except Exception as e:
            self.thumb_label.config(text="无法显示缩略图")
    
    def update_info_display(self):
        if self.image_list:
            total = len(self.image_list)
            current = self.current_index + 1
            image_name = os.path.basename(self.current_image_path) if self.current_image_path else ""
            
            # 更新文件信息
            self.file_info_label.config(
                text=f"文件：{image_name} | 第 {current}/{total} 张"
            )
            
            # 更新列表统计
            self.list_info_label.config(
                text=f"保存：{len(self.save_list)}"
            )
        else:
            self.file_info_label.config(text="")
            self.list_info_label.config(text="")
            self.exif_text.config(text="")
    
    def update_status(self):
        if self.image_list and self.current_image_path:
            total = len(self.image_list)
            current = self.current_index + 1
            image_name = os.path.basename(self.current_image_path)
            self.status_label.config(
                text=f"当前：{image_name} | 进度：{current}/{total} | 保存：{len(self.save_list)}"
            )
        else:
            self.status_label.config(text="请先选择文件夹")

def main():
    root = tk.Tk()
    app = PictureReviewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()