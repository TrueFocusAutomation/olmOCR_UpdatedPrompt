import datetime
import hashlib
import json
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field

class OCRFrontMatter(BaseModel):
    """
    Metadata extracted by the model. 
    Fields are made Optional to prevent pipeline failure if the model omits them.
    """
    primary_language: Optional[str] = Field(None, description="The primary language of the document")
    is_readable: Optional[bool] = Field(True, description="Whether the page is readable")
    is_blank: Optional[bool] = Field(False, description="Whether the page is blank")
    is_understandable: Optional[bool] = Field(True, description="Whether the page content is understandable")

class OCRPageResponse(BaseModel):
    """
    The structured response expected from the model.
    """
    front_matter: OCRFrontMatter
    natural_text: str = Field(..., description="The main text content extracted from the page")

@dataclass(frozen=True)
class PdfOutput:
    path: str
    text: str
    total_pdf_pages: int
    processed_pdf_pages: int

    def mk_dolma_doc(self, **kwargs) -> str:
        metadata = {
            "Source-File": self.path,
            "pdf-pages": self.processed_pdf_pages,
            "pdf-total-pages": self.total_pdf_pages,
            # Kwargs are added as extra metadata
            **kwargs,
        }
        # Create a stable ID based on the content
        id_ = hashlib.sha1(self.text.encode()).hexdigest()

        dolma_doc = {
            "id": id_,
            "text": self.text,
            "source": "olmocr",
            "added": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "created": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "metadata": metadata,
        }

        return json.dumps(dolma_doc)
