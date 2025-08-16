from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
                            
class AboutWindow(QDialog):
    """About dialog window"""
    def __init__(self, data, logo_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setMinimumSize(500, 300)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Description
        description_label = QLabel(f"<b>{data['description']}</b>")
        description_label.setWordWrap(True)
        description_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(description_label)
        
        # Add separator
        separator = QLabel()
        separator.setFrameShape(QLabel.HLine)
        separator.setFrameShadow(QLabel.Sunken)
        layout.addWidget(separator)
        
        # Package info
        package_label = QLabel(f"Package: {data['package']}")
        package_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        package_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(package_label)
        
        # Program info
        program_label = QLabel(f"Program: {data['program_name']}")
        program_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        program_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(program_label)
        
        # Version info
        version_label = QLabel(f"Version: {data['version']}")
        version_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        version_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(version_label)
        
        # Author info
        author_label = QLabel(f"Author: {data['author']}")
        author_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        author_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(author_label)
        
        # Email info
        email_label = QLabel(f"Email: <a href=\"mailto:{data['email']}\">{data['email']}</a>")
        email_label.setTextInteractionFlags(Qt.TextSelectableByMouse| Qt.LinksAccessibleByMouse)
        email_label.setOpenExternalLinks(True)
        email_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(email_label)
        
        # Add another separator
        separator2 = QLabel()
        separator2.setFrameShape(QLabel.HLine)
        separator2.setFrameShadow(QLabel.Sunken)
        layout.addWidget(separator2)
        
        # Source URL
        source_label = QLabel(f"Source: <a href=\"{data['url_source']}\">{data['url_source']}</a>")
        source_label.setTextInteractionFlags(Qt.TextSelectableByMouse| Qt.LinksAccessibleByMouse)
        source_label.setOpenExternalLinks(True)
        source_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(source_label)
        
        # Doc URL
        doc_label = QLabel(f"Documentation: <a href=\"{data['url_doc']}\">{data['url_doc']}</a>")
        doc_label.setTextInteractionFlags(Qt.TextSelectableByMouse| Qt.LinksAccessibleByMouse)
        doc_label.setOpenExternalLinks(True)
        doc_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(doc_label)
        
        # Funding URL
        funding_label = QLabel(f"Funding: <a href=\"{data['url_funding']}\">{data['url_funding']}</a>")
        funding_label.setTextInteractionFlags(Qt.TextSelectableByMouse| Qt.LinksAccessibleByMouse)
        funding_label.setOpenExternalLinks(True)
        funding_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(funding_label)
        
        # Bugs URL
        bugs_label = QLabel(f"Bugs: <a href=\"{data['url_bugs']}\">{data['url_bugs']}</a>")
        bugs_label.setTextInteractionFlags(Qt.TextSelectableByMouse| Qt.LinksAccessibleByMouse)
        bugs_label.setOpenExternalLinks(True)
        bugs_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(bugs_label)
        
        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

def show_about_window(data, logo_path):
    dialog = AboutWindow(data, logo_path)
    dialog.exec_()

