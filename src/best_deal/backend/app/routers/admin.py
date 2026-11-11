"""
Administrative routes for the Todo application.

Description:
    This module provides endpoints used to manage application users and
    enforce administrator access.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status
from typing import Annotated, Literal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime
from ..models import Users, GlobalDeals, UserDeals
from ..database import get_db
from .auth import get_current_user

"""
Configurations
"""
router = APIRouter(
     prefix='/admin',
     tags=['admin']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/global-deals", status_code=status.HTTP_200_OK)
def search_global_deals(
    user: user_dependency,
    db: db_dependency,
    product_title: str | None = Query(default=None, min_length=1),
    category: str | None = Query(default=None),
    market: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    actual_price_min: Decimal | None = Query(default=None, ge=0),
    actual_price_max: Decimal | None = Query(default=None, ge=0),
    estimated_price_min: Decimal | None = Query(default=None, ge=0),
    estimated_price_max: Decimal | None = Query(default=None, ge=0),
    discount_min: Decimal | None = Query(default=None, ge=0, le=100),
    discount_max: Decimal | None = Query(default=None, ge=0, le=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        "actual_price",
        "estimated_price",
        "discount",
        "created_at"
    ] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc"
):

    """
    Search and filter global deals based on multiple criteria.

    Args:
        user: Authenticated administrator claims.
        db: Database session.
        product_title: Optional product title to search for.
        category: Optional product category filter.
        market: Optional market or country filter.
        currency: Optional currency filter.
        actual_price_min: Minimum actual product price.
        actual_price_max: Maximum actual product price.
        estimated_price_min: Minimum estimated product price.
        estimated_price_max: Maximum estimated product price.
        discount_min: Minimum discount percentage.
        discount_max: Maximum discount percentage.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        sort_by: Field used to sort the results.
        sort_order: Sorting direction, ascending or descending.

    Returns:
        A list of global deals matching the specified filters,
        sorted and paginated according to the provided parameters.
    """

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if user.get("role")!= "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission is denied')

    query = db.query(GlobalDeals)

    if product_title:
        query = query.filter(
            GlobalDeals.product_title.ilike(
                f"%{product_title.strip()}%"
            )
        )

    if category:
        query = query.filter(
            GlobalDeals.category == category.strip()
        )

    if market:
        query = query.filter(
            GlobalDeals.market == market.strip()
        )

    if currency:
        query = query.filter(
            GlobalDeals.currency == currency.strip().upper()
        )

    if actual_price_min is not None:
        query = query.filter(
            GlobalDeals.actual_price >= actual_price_min
        )

    if actual_price_max is not None:
        query = query.filter(
            GlobalDeals.actual_price <= actual_price_max
        )

    if estimated_price_min is not None:
        query = query.filter(
            GlobalDeals.estimated_price >= estimated_price_min
        )

    if estimated_price_max is not None:
        query = query.filter(
            GlobalDeals.estimated_price <= estimated_price_max
        )

    if discount_min is not None:
        query = query.filter(
            GlobalDeals.discount >= discount_min
        )

    if discount_max is not None:
        query = query.filter(
            GlobalDeals.discount <= discount_max
        )

    sort_column = getattr(GlobalDeals, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    results = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No global deals found matching the criteria.")
    return results




@router.get('/user-deals', status_code=status.HTTP_200_OK)
def search_user_deals(
    user: user_dependency,
    db: db_dependency,
    user_id: int | None = Query(default=None, gt=0),
    username: str | None = Query(default=None, min_length=1),
    email: str | None = Query(default=None, min_length=1),
    deal_id: int | None = Query(default=None, gt=0),
    is_seen: bool | None = Query(default=None),
    is_saved: bool | None = Query(default=None),
    recommended_from: datetime | None = Query(default=None),
    recommended_to: datetime | None = Query(default=None),
    product_title: str | None = Query(default=None, min_length=1),
    category: str | None = Query(default=None),
    market: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    actual_price_min: Decimal | None = Query(default=None, ge=0),
    actual_price_max: Decimal | None = Query(default=None, ge=0),
    discount_min: Decimal | None = Query(default=None, ge=0, le=100),
    discount_max: Decimal | None = Query(default=None, ge=0, le=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        "recommended_at",
        "actual_price",
        "discount"
    ] = "recommended_at",
    sort_order: Literal["asc", "desc"] = "desc"
):
    """
    Search and filter user deals based on multiple criteria.

    Args:
        user: Authenticated administrator claims.
        db: Database session.
        user_id: Optional user identifier.
        username: Optional username search.
        email: Optional email search.
        deal_id: Optional global deal identifier.
        is_seen: Filter by whether the user has seen the deal.
        is_saved: Filter by whether the user has saved the deal.
        recommended_from: Earliest recommendation date.
        recommended_to: Latest recommendation date.
        product_title: Optional product title search.
        category: Optional product category filter.
        market: Optional market filter.
        currency: Optional currency filter.
        actual_price_min: Minimum actual price.
        actual_price_max: Maximum actual price.
        discount_min: Minimum discount percentage.
        discount_max: Maximum discount percentage.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        sort_by: Field used to sort the results.
        sort_order: Sorting direction.

    Returns:
        A list of matching user-deal recommendation records.
    """

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if user.get("role")!= "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission is denied')

    query = (
        db.query(UserDeals)
        .join(GlobalDeals, UserDeals.deal_id == GlobalDeals.id)
        .join(Users, UserDeals.user_id == Users.id)
    )

    if user_id is not None:
        query = query.filter(UserDeals.user_id == user_id)

    if username:
        query = query.filter(
            Users.username.ilike(f"%{username.strip()}%")
        )

    if email:
        query = query.filter(
            Users.email.ilike(f"%{email.strip()}%")
        )

    if deal_id is not None:
        query = query.filter(UserDeals.deal_id == deal_id)

    if is_seen is not None:
        query = query.filter(UserDeals.is_seen == is_seen)

    if is_saved is not None:
        query = query.filter(UserDeals.is_saved == is_saved)

    if recommended_from is not None:
        query = query.filter(
            UserDeals.recommended_at >= recommended_from
        )

    if recommended_to is not None:
        query = query.filter(
            UserDeals.recommended_at <= recommended_to
        )

    if product_title:
        query = query.filter(
            GlobalDeals.product_title.ilike(
                f"%{product_title.strip()}%"
            )
        )

    if category:
        query = query.filter(GlobalDeals.category == category.strip())

    if market:
        query = query.filter(GlobalDeals.market == market.strip())

    if currency:
        query = query.filter(
            GlobalDeals.currency == currency.strip().upper()
        )

    if actual_price_min is not None:
        query = query.filter(
            GlobalDeals.actual_price >= actual_price_min
        )

    if actual_price_max is not None:
        query = query.filter(
            GlobalDeals.actual_price <= actual_price_max
        )

    if discount_min is not None:
        query = query.filter(
            GlobalDeals.discount >= discount_min
        )

    if discount_max is not None:
        query = query.filter(
            GlobalDeals.discount <= discount_max
        )

    sort_columns = {
        "recommended_at": UserDeals.recommended_at,
        "actual_price": GlobalDeals.actual_price,
        "discount": GlobalDeals.discount
    }

    sort_column = sort_columns[sort_by]
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    results = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No global deals found matching the criteria.")
    return results



@router.delete('/global-deals/delete-deal/{deal_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_global_deal(user: user_dependency, db: db_dependency, deal_id: int = Path(gt=0)):
    """
    Delete any global deal item for an administrator.

    Args:
        user: Authenticated administrator claims.
        db: Database session.
        deal_id: Global deal identifier.
    """

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if user.get("role")!= "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission is denied')

    delete_global_deal = db.query(GlobalDeals).filter(GlobalDeals.id == deal_id).first()

    if delete_global_deal is None:
        raise HTTPException(status_code=404, detail='Global deal not found')

    db.delete(delete_global_deal)
    db.commit()
