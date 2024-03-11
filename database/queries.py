from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from database.database import session
from database.models import Category, Website

NO_CATEGORY_ID = 1


def get_all_websites() -> list[Website] | str:
    """
    Retrieves all websites from the database.

    Returns:
        list[Website] | str: A list of websites if successful, otherwise an error message.
    """
    try:
        with session:
            db_websites = (
                session.query(Website)
                .options(joinedload(Website.category))
                .order_by(desc(Website.id))
                .all()
            )
            return db_websites
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error retrieving websites: {e}")


def get_single_website(site_id: int) -> Any | None:
    """
    Retrieves a single website from the database based on the given site ID.

    Parameters:
        site_id (int): The ID of the website to retrieve.

    Returns:
        Any | None: The website object if found, otherwise None.

    Raises:
        ValueError: If there is an error retrieving the website ID.
    """
    try:
        with session:
            db_site = (
                session.query(Website)
                .options(joinedload(Website.category))
                .filter_by(id=site_id)
                .first()
            )
            return db_site
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error retrieving website id: {e}")


def submit_new_website(
        title: str,
        url: str,
        icon: str,
        category: str | None = None):
    """
    Submits a new website to the database.

    Args:
        title (str): The title of the website.
        url (str): The URL of the website.
        icon (str): The icon of the website.
        category (str | None, optional): The category of the website. Defaults to None.

    Returns:
        Website: The newly submitted website.

    Raises:
        ValueError: If there was an error saving the website to the database.
    """
    try:
        with session:
            db_category = (
                session.query(Category)
                .filter(Category.title == category.capitalize())
                .first()
            )
            db_site = Website(title=title, url=url, category=db_category, icon=icon)
            session.add(db_site)
            session.commit()
            return db_site
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error saving website: {e}")


def update_single_website(
        site_id: int,
        title: str,
        url: str,
        icon: str,
        category: str | None = None):
    """
    Updates a single website in the database with the given information.

    Args:
        site_id (int): The ID of the website to update.
        title (str): The new title of the website.
        url (str): The new URL of the website.
        icon (str): The new icon of the website.
        category (str | None, optional): The new category of the website. Defaults to None.

    Returns:
        Website: The updated website object.

    Raises:
        ValueError: If there is an error updating the website.
    """
    try:
        with session:
            db_site = session.query(Website).filter_by(id=site_id).first()
            db_category = (
                session.query(Category)
                .filter(Category.title == category.capitalize())
                .first()
            )
            db_site.title = title
            db_site.url = url
            db_site.icon = icon
            db_site.category = db_category or session.query(Category).filter_by(id=1).first()
            session.commit()
            return db_site
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error updating website: {e}")


def get_categories() -> list[Category]:
    """
    Retrieves a list of categories from the database.

    Returns:
        list[Category]: A list of Category objects representing the categories.

    Raises:
        ValueError: If there is an error retrieving the categories from the database.
    """
    try:
        with session:
            db_categories = session.query(Category).order_by(desc(Category.id)).all()
            return db_categories
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error retrieving categories: {e}")


def add_new_category(title: str) -> int:
    """
    Adds a new category to the database.

    Args:
        title (str): The title of the category.

    Returns:
        int: The ID of the newly added category.

    Raises:
        ValueError: If there was an error adding the new category to the database.
    """
    try:
        with session:
            db_category = Category(title=title.capitalize())
            session.add(db_category)
            session.commit()
            return db_category.id
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error adding new category: {e}")


def delete_category(category_title: str) -> None:
    """
    Deletes a category from the database.

    Args:
        category_title (str): The title of the category to be deleted.

    Raises:
        ValueError: If the category does not exist or if there is an error deleting the category.

    Returns:
        None
    """
    try:
        with session:
            cat = session.query(Category).filter_by(title=category_title).first()
            if not cat:
                raise ValueError(f"Category {category_title} not exist.")

            # Обновляем их категорию на "NO CATEGORY"
            (
                session.query(Website)
                .filter_by(category_id=cat.id)
                .update({Website.category_id: NO_CATEGORY_ID})
            )
            session.delete(cat)
            session.commit()
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error deleting category: {e}")


def delete_website(site_id: int) -> Website:
    try:
        with session:
            db_site = session.query(Website).filter_by(id=site_id).first()
            session.delete(db_site)
            session.commit()
            return db_site
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error deleting website: {e}")
