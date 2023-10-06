import logging
import re
import os
from datetime import datetime
from urllib.parse import urlsplit
import requests
from PIL import Image
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from duckduckgo_search import ddg_images

logger = logging.getLogger(__name__)

Base = declarative_base()

# Many-to-Many join table
image_tags = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", Integer, ForeignKey("image_metadata.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    description = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    file_type = Column(String)
    file_size = Column(Integer)
    file_path = Column(String)
    retrieved = Column(Boolean)
    tags = relationship("Tag", secondary=image_tags, back_populates="images")

    # Utility function to add a tag
    def add_tag(self, session, tag_name):
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            session.commit()
        if tag not in self.tags:
            self.tags.append(tag)
            session.commit()

    # Utility function to remove a tag
    def remove_tag(self, session, tag_name):
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if tag and tag in self.tags:
            self.tags.remove(tag)
            session.commit()


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    images = relationship("ImageMetadata", secondary=image_tags, back_populates="tags")


engine = create_engine("sqlite:///images.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def sanitize_filename(filename):
    """
    Sanitize the filename to make it file-system friendly.
    """
    # Convert to lowercase
    s = filename.lower()
    # Replace non-alphanumeric characters with underscores
    s = re.sub(r"[^a-z0-9]", "_", s)
    # Trim to a maximum of 50 characters (optional, can adjust as needed)
    s = s[:50]
    return s


def collect_metadata(keyword, tags=[]):
    session = Session()
    results = ddg_images(keyword, max_results=None)

    for result in results:
        sanitized_title = sanitize_filename(result.get("title", ""))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        metadata = ImageMetadata(
            url=result["image"],
            title=result.get("title", ""),
            description=result.get("description", ""),
            width=result.get("width", None),
            height=result.get("height", None),
            file_type=result.get("file_type", ""),
            file_size=result.get("file_size", None),
            file_path="",  # Will be updated once the image is downloaded
            retrieved=False,
        )
        session.add(metadata)
        session.commit()

        # Constructing file name after the metadata is committed to get the ID
        base_url = "{0.scheme}://{0.netloc}{0.path}".format(urlsplit(result["image"]))
        file_extension = os.path.splitext(base_url)[1]
        file_name = f"{sanitized_title}_{timestamp}_{metadata.id}{file_extension}"
        metadata.file_path = file_name

        # Add each tag from the provided list
        for tag_name in tags:
            metadata.add_tag(
                session, tag_name.strip()
            )  # Using strip to remove any leading/trailing whitespace
        session.commit()

    session.close()


def extract_image_metadata(img_path):
    """Extract metadata from the image."""
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            file_format = img.format
            mode = img.mode

        description = (
            f"Resolution: {width}x{height}, Format: {file_format}, Mode: {mode}"
        )
        return description
    except Exception as e:
        logger.error(f"Error extracting image metadata: {e}")
        return None


def download_images(folder="downloaded_images"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    session = Session()
    images_to_retrieve = session.query(ImageMetadata).filter_by(retrieved=False).all()
    total_images = len(images_to_retrieve)

    for index, image_data in enumerate(images_to_retrieve, 1):
        try:
            response = requests.get(image_data.url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(folder, image_data.file_path)

                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                # Extract metadata from the downloaded image
                description = extract_image_metadata(file_path)

                # Update the image_data with the file_path, mark it as retrieved, and update the description
                image_data.retrieved = True
                if description:
                    image_data.description = description

                # Commit after each successful image download
                session.commit()

                # Print progress
                if not index % 10:
                    print(f"Downloaded {index}/{total_images} images.")

        except requests.RequestException as e:
            print(f"Error downloading {image_data.url}: {e}")

    session.close()


if __name__ == "__main__":
    # Usage
    # collect_metadata("musicians with cats", ["cats", "musicians"])
    # collect_metadata("musicians with dogs", ["dogs", "musicians"])
    # collect_metadata("musicians with snakes", ["snakes", "musicians"])
    # collect_metadata("musicians with cats and dogs", ["cats", "dogs", "musicians"])
    collect_metadata("musicians with birds", ["birds", "musicians"])
    download_images()
    # Usage example:
    # collect_metadata("cute cats", tags=['cute', 'animals'])
