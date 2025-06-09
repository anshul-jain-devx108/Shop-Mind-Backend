# from flask import Blueprint, request, jsonify
# from ..models import Product
# from .. import db
# from flask_jwt_extended import jwt_required

# products_bp = Blueprint('products', __name__)

# @products_bp.route('', methods=['GET'])
# @jwt_required()
# def get_products():
#     # Filtering params
#     category = request.args.get('category')
#     min_price = request.args.get('minPrice', type=float)
#     max_price = request.args.get('maxPrice', type=float)
#     rating = request.args.get('rating', type=float)
#     page = request.args.get('page', 1, type=int)
#     limit = request.args.get('limit', 20, type=int)

#     query = Product.query

#     if category:
#         query = query.filter(Product.category.ilike(f'%{category}%'))
#     if min_price is not None:
#         query = query.filter(Product.price >= min_price)
#     if max_price is not None:
#         query = query.filter(Product.price <= max_price)
#     if rating is not None:
#         query = query.filter(Product.rating >= rating)

#     total = query.count()
#     total_pages = (total + limit - 1) // limit

#     products = query.offset((page -1)*limit).limit(limit).all()

#     products_data = [{
#         'id': p.id,
#         'name': p.name,
#         'category': p.category,
#         'price': p.price,
#         'rating': p.rating,
#         'description': p.description
#     } for p in products]

#     return jsonify({
#         'products': products_data,
#         'total': total,
#         'page': page,
#         'totalPages': total_pages
#     })

# @products_bp.route('/search', methods=['GET'])
# @jwt_required()
# def search_products():
#     q = request.args.get('q')
#     page = request.args.get('page', 1, type=int)
#     limit = request.args.get('limit', 20, type=int)

#     if not q:
#         return jsonify({'error': 'Missing search query'}), 400

#     query = Product.query.filter(Product.name.ilike(f'%{q}%'))
#     total = query.count()
#     total_pages = (total + limit -1)//limit
#     products = query.offset((page -1)*limit).limit(limit).all()

#     products_data = [{
#         'id': p.id,
#         'name': p.name,
#         'category': p.category,
#         'price': p.price,
#         'rating': p.rating,
#         'description': p.description
#     } for p in products]

#     return jsonify({
#         'products': products_data,
#         'total': total,
#         'page': page,
#         'totalPages': total_pages
#     })


from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from ..models import Product
from .. import db
from flask_jwt_extended import jwt_required

products_bp = Blueprint('products', __name__)

@products_bp.route('/search', methods=['GET'])
@jwt_required()
def search_products():
    q = request.args.get('q')
    if not q:
        return jsonify({'error': 'Missing search query'}), 400

    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({"error": "Page and limit must be integers"}), 400

    query = Product.query.filter(
        or_(
            Product.name.ilike(f'%{q}%'),
            Product.description.ilike(f'%{q}%')
        )
    )

    total = query.count()
    total_pages = (total + limit - 1) // limit
    products = query.offset((page - 1) * limit).limit(limit).all()

    products_data = [{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'rating': p.rating,
        'description': p.description
    } for p in products]

    return jsonify({
        'products': products_data,
        'total': total,
        'page': page,
        'totalPages': total_pages
    })
