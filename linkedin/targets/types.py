
from dataclasses import dataclass


@dataclass
class Connection:
    name: str = None
    headline: str = None
    profile_link: str = None
    photo_link: str = None
    connected_date: str = None

@dataclass
class Job:
    job_title: str = None
    job_link: str = None
    company: str = None
    location: str = None
    time_since_posted: str = None

@dataclass
class Post:
    author_name: str = None
    author_profile_photo_url: str = None
    time_since_posted: str = None
    post_content: str = None   

@dataclass
class Person:
    name: str = None
    profile_photo_url: str = None
    headline: str = None
    location: str = None

@dataclass
class Company:
    company_name: str = None
    headline: str = None
    follower_count: int = None
    description: str = None

@dataclass
class Group:
    group_name: str = None
    total_members: int = None
    description: str = None

@dataclass
class Product:
    product_name: str = None
    headline: str = None
    description: str = None




