#!/usr/bin/python3

import sys
import subprocess
import tempfile
import os
import signal

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QLabel, QSplitter, QToolBar,
    QAction, QVBoxLayout, QWidget, QProgressBar, QFileDialog, QScrollArea, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QPixmap, QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QSize

import graphviz_code_viewer.about as about
import graphviz_code_viewer.modules.configure as configure 
from graphviz_code_viewer.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
from graphviz_code_viewer.modules.wabout import show_about_window


# Path to config file
CONFIG_PATH = os.path.join(os.path.expanduser("~"),".config",about.__package__,"config.json")

DEFAULT_CONTENT={   "error_loading_svg": "Error loading SVG file",
                    "font_size": 11,
                    "font_name": "Courier",
                    "window_width": 1200,
                    "window_height": 700,
                    "action_compile":"Compile",
                    "action_compile_tooltip": "Compile the DOT file",
                    "action_open":"Open",
                    "action_open_tooltip": "Open the DOT file",
                    "action_save":"Save",
                    "action_save_tooltip": "Save the DOT file",
                    "action_saveas":"Save as",
                    "action_saveas_tooltip": "Save the DOT file as",
                    "action_saveimg":"Save image",
                    "action_saveimg_tooltip": "Save the output image",
                    "action_configure": "Configure",
                    "action_configure_tooltip": "Open the configure Json file",
                    "action_about": "About",
                    "action_about_tooltip": "About the program",
                    "action_coffee": "Coffee",
                    "action_coffee_tooltip": "Buy me a coffee (TrucomanX)",
                    "warning":"Warning",
                    "no_image_available":"No image available to save. Compile the code first.",
                    "save_image":"Save image",
                    "image_save_in":"Image saves in:",
                    "open_dot_file":"Open DOT file",
                    "loaded_file":"Loaded file:",
                    "error_opening_dot_file":"Error opening DOT file:",
                    "exist_dot_file":"The file already exists and will not be overcrowded:",
                    "save_dot_file": "Save DOT file",
                    "dot_file_dot": "DOT File (*.dot)",
                    "saved_file":"Saved file:",
                    "error":"Error",
                    "error_saving_file":"It was not possible to save the file:",
                    "error_compilation":"Error in graphviz compilation."
                }

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ---------------------------
# Syntax Highlighter
# ---------------------------
class GraphvizHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, rules_dict):
        super().__init__(parent)
        self.rules = []
        for key, data in rules_dict.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(data["color"]))
            if data["bold"]:
                fmt.setFontWeight(QFont.Bold)
            self.rules.append((key, fmt))

    def highlightBlock(self, text):
        for keyword, fmt in self.rules:
            index = text.find(keyword)
            while index != -1:
                length = len(keyword)
                self.setFormat(index, length, fmt)
                index = text.find(keyword, index + length)

# ---------------------------
# Worker thread para compilar Graphviz
# ---------------------------
class CompileThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, dot_code, output_file):
        super().__init__()
        self.dot_code = dot_code
        self.output_file = output_file

    def run(self):
        self.progress.emit(10)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".dot")
        tmp_dot = temp_file.name
        temp_file.close()
        
        with open(tmp_dot, "w") as f:
            f.write(self.dot_code)
        self.progress.emit(50)
        try:
            subprocess.run(
                ["dot", "-Tsvg", tmp_dot, "-o", self.output_file],
                check=True
            )
            self.progress.emit(100)
            self.finished.emit(self.output_file)
        except subprocess.CalledProcessError:
            self.finished.emit("")
            
        if os.path.exists(tmp_dot):
            os.remove(tmp_dot)


# ---------------------------
# Widget da imagem com zoom/move
# ---------------------------


class SvgViewer(QScrollArea):
    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.renderer = None
        self.zoom = 1.0
        self.offset = None

    def load_image(self, path):
        self.renderer = QSvgRenderer(path)
        if not self.renderer.isValid():
            print(CONFIG["error_loading_svg"])
            return
        self.zoom = 1.0
        self.update_display()

    def update_display(self):
        if self.renderer:
            # calcular o tamanho do SVG considerando o zoom
            size = self.renderer.defaultSize() * self.zoom
            size = QSize(max(1, size.width()), max(1, size.height()))
            
            # criar um pixmap transparente do tamanho desejado
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)
            
            # renderizar o SVG diretamente no pixmap
            painter = QPainter(pixmap)
            self.renderer.render(painter)
            painter.end()
            
            self.label.setPixmap(pixmap)
            self.label.resize(pixmap.size())

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9
        self.zoom *= factor
        self.update_display()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset:
            delta = event.pos() - self.offset
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.offset = event.pos()

    def mouseReleaseEvent(self, event):
        self.offset = None



# ---------------------------
# Editor de texto com zoom
# ---------------------------
class TextEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont(CONFIG["font_name"], CONFIG["font_size"]))
        self.zoom_factor = 1.0

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.1 if angle > 0 else 0.9
            self.zoom_factor *= factor
            font = self.font()
            font.setPointSizeF(CONFIG["font_size"] * self.zoom_factor)
            self.setFont(font)
        else:
            super().wheelEvent(event)

# ---------------------------
# Main Window
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self, filepath):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        # input file path
        if os.path.exists(filepath):
            self.input_filepath=str(filepath)
        else:
            self.input_filepath=""

        # Criar um arquivo temporário único para o SVG
        temp_svg = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
        self.temp_svg_path = temp_svg.name
        temp_svg.close()  # fecha o arquivo, vamos escrever nele depois


        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(self.icon_path)) 
        

        # Toolbar
        self.func_toolbar()


        # Criar status bar 
        self.status = self.statusBar()
        
        # Editor e visualizador
        self.editor = TextEditor()
        syntax_rules = {
            "digraph": {"color": "blue", "bold": True},
            "->": {"color": "darkRed", "bold": True},
            "=": {"color": "darkRed", "bold": True},
            "\"": {"color": "darkMagenta", "bold": True},
            "[": {"color": "black", "bold": True},
            "]": {"color": "black", "bold": True},
            "{": {"color": "darkGreen", "bold": True},
            "}": {"color": "darkGreen", "bold": True},
            ";": {"color": "darkGray", "bold": True}
        }
        self.highlighter = GraphvizHighlighter(self.editor.document(), syntax_rules)
        self.viewer = SvgViewer()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.viewer)
        splitter.setSizes([int(CONFIG["window_width"]/2), int(CONFIG["window_width"]-CONFIG["window_width"]/2)])

        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setValue(0)

        # Layout central
        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.progress)
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        if os.path.exists(self.input_filepath):
            self.load_dot(filepath=self.input_filepath)

    def func_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        
        # Compile
        compile_action = QAction(QIcon.fromTheme("media-playback-start"),CONFIG["action_compile"], self)
        compile_action.setToolTip(CONFIG["action_compile_tooltip"])
        compile_action.triggered.connect(self.compile_dot)
        toolbar.addAction(compile_action)
        
        # Load
        load_action = QAction(QIcon.fromTheme("document-open"),CONFIG["action_open"], self)
        load_action.setToolTip(CONFIG["action_open_tooltip"])
        load_action.triggered.connect(lambda: self.load_dot(filepath=""))
        toolbar.addAction(load_action)
        
        # Save
        save_action = QAction(QIcon.fromTheme("document-save"),CONFIG["action_save"], self)
        save_action.setToolTip(CONFIG["action_save_tooltip"])
        save_action.triggered.connect(lambda: self.save_dot(from_input=True,exist_ok=True))
        toolbar.addAction(save_action)

        # Save as
        saveas_action = QAction(QIcon.fromTheme("document-save-as"),CONFIG["action_saveas"], self)
        saveas_action.setToolTip(CONFIG["action_saveas_tooltip"])
        saveas_action.triggered.connect(lambda: self.save_dot(from_input=False,exist_ok=False))
        toolbar.addAction(saveas_action)
        
        # Save Image
        save_image_action = QAction(QIcon.fromTheme("image-x-generic"), CONFIG["action_saveimg"], self)
        save_image_action.setToolTip(CONFIG["action_saveimg_tooltip"])
        save_image_action.triggered.connect(self.save_image)
        toolbar.addAction(save_image_action)
        

        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        # 
        self.configure_action = QAction(QIcon.fromTheme("document-properties"), CONFIG["action_configure"], self)
        self.configure_action.setToolTip(CONFIG["action_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)
        toolbar.addAction(self.configure_action)
        
        #
        self.about_action = QAction(QIcon.fromTheme("help-about"), CONFIG["action_about"], self)
        self.about_action.setToolTip(CONFIG["action_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        toolbar.addAction(self.about_action)
        
        # Coffee
        self.coffee_action = QAction(QIcon.fromTheme("emblem-favorite"), CONFIG["action_coffee"], self)
        self.coffee_action.setToolTip(CONFIG["action_coffee_tooltip"])
        self.coffee_action.triggered.connect(self.on_coffee_action_click)
        toolbar.addAction(self.coffee_action)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    
    def open_configure_editor(self):
        if os.name == 'nt':  # Windows
            os.startfile(CONFIG_PATH)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', CONFIG_PATH])

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def save_image(self):
        # Verifica se existe uma imagem carregada
        if not self.viewer.renderer or not self.viewer.renderer.isValid():
            QMessageBox.warning(self, CONFIG["warning"], CONFIG["no_image_available"])
            return

        # Pergunta onde salvar
        path, _ = QFileDialog.getSaveFileName(
            self,
            CONFIG["save_image"],
            "",
            "SVG File (*.svg);;PNG File (*.png)"
        )

        if not path:
            return  # cancelado

        # Se for PNG, renderizar e salvar
        if path.lower().endswith(".png"):
            size = self.viewer.renderer.defaultSize()
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            self.viewer.renderer.render(painter)
            painter.end()
            pixmap.save(path, "PNG")
        else:  # SVG
            # Copia o arquivo temporário para o destino
            import shutil
            shutil.copyfile(self.temp_svg_path, path)

        self.status.showMessage(CONFIG["image_save_in"]+" "+path, 5000)

        
    def load_dot(self, filepath=""):
        
        if not os.path.exists(filepath):
            # Abre uma caixa de diálogo para selecionar arquivos .dot
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                CONFIG["open_dot_file"],
                "",
                CONFIG["dot_file_dot"]
            )

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.editor.setPlainText(content)  # carrega o conteúdo no QPlainTextEdit
                    self.input_filepath=str(filepath)
                    self.status.showMessage(CONFIG["loaded_file"]+" "+self.input_filepath, 5000)
            except Exception as e:
                print(CONFIG["error_opening_dot_file"]+f"{e}")

    def save_dot(self, from_input=True, exist_ok=True):
        path=None
        if from_input:
            path = self.input_filepath
        
        # Se o path foi fornecido e já existe, não sobrescreve
        if path and os.path.exists(path) and exist_ok==False:
            QMessageBox.warning(self, CONFIG["warning"], CONFIG["exist_dot_file"] + "\n" + path)
            return

        # Se path não foi fornecido ou não existe, abre diálogo para salvar
        if not path or len(path)==0:
            path, _ = QFileDialog.getSaveFileName(
                self,
                CONFIG["save_dot_file"],
                "",
                CONFIG["dot_file_dot"]
            )

            if not path:  # usuário cancelou
                return

        # Garantir que o arquivo termine com .dot
        if not path.lower().endswith(".dot"):
            path += ".dot"

        try:
            with open(path, "w", encoding="utf-8") as f:
                content = self.editor.toPlainText()
                f.write(content)
                self.status.showMessage(CONFIG["saved_file"]+" "+path, 5000)
        except Exception as e:
            QMessageBox.critical(self, CONFIG["erro"], CONFIG["error_saving_file"]+"\n"+ e)
            
    def compile_dot(self):
        dot_code = self.editor.toPlainText()
        self.progress.setValue(0)

        self.thread = CompileThread(dot_code, self.temp_svg_path)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.show_image)
        self.thread.start()

    def show_image(self, path):
        if path:
            self.viewer.load_image(path)
        else:
            print(CONFIG["error_compilation"])

# ---------------------------
# Run
# ---------------------------
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    filepath = ""
    if(len(sys.argv)==2):
        if sys.argv[1] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
            
        if sys.argv[1] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return

        if os.path.exists(sys.argv[1]):
            filepath = sys.argv[1]
    else:
        for n in range(len(sys.argv)):
            if sys.argv[n] == "--autostart":
                create_desktop_directory(overwrite = True)
                create_desktop_menu(overwrite = True)
                create_desktop_file('~/.config/autostart', overwrite=True)
                return
            if sys.argv[n] == "--applications":
                create_desktop_directory(overwrite = True)
                create_desktop_menu(overwrite = True)
                create_desktop_file('~/.local/share/applications', overwrite=True)
                return

    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    
    window = MainWindow(filepath)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

