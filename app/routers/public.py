"""
Public endpoints for marketing, SEO, and guest access.

This router handles public-facing endpoints that don't require authentication,
including landing pages, property listings, and guest booking flows.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, and_, func
from typing import List, Optional, Dict, Any
from datetime import date
import uuid

from app.core.database import get_session
from app.services.search_service import SearchService
from app.services.booking_service import BookingService
from app.models.property import Property
from app.models.organization import Organization
from app.models.booking import Booking
from app.utils.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/", response_class=HTMLResponse)
def landing_page():
    """Main landing page for the hotel booking platform."""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hotel Booking System - Find Your Perfect Stay</title>
        <meta name="description" content="Book hotels worldwide with our comprehensive hotel booking system. Find the best deals and perfect accommodations for your next trip.">
        <meta name="keywords" content="hotel booking, accommodation, travel, hotels, reservations">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 20px; text-align: center; }
            .hero h1 { font-size: 3em; margin-bottom: 20px; }
            .hero p { font-size: 1.2em; margin-bottom: 30px; }
            .search-form { background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .form-row { display: flex; gap: 15px; margin-bottom: 20px; }
            .form-group { flex: 1; }
            .form-group label { display: block; margin-bottom: 5px; color: #333; font-weight: bold; }
            .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            .search-btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; width: 100%; }
            .search-btn:hover { background: #5a6fd8; }
            .features { padding: 80px 20px; background: #f8f9fa; }
            .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; max-width: 1200px; margin: 0 auto; }
            .feature { text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .feature h3 { color: #667eea; margin-bottom: 15px; }
            .cta { background: #667eea; color: white; padding: 80px 20px; text-align: center; }
            .cta-btn { background: white; color: #667eea; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>Find Your Perfect Stay</h1>
            <p>Discover amazing hotels and accommodations worldwide</p>
            
            <div class="search-form">
                <form action="/public/search" method="get">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="city">Destination</label>
                            <input type="text" id="city" name="city" placeholder="Where are you going?" required>
                        </div>
                        <div class="form-group">
                            <label for="check_in">Check-in</label>
                            <input type="date" id="check_in" name="check_in" required>
                        </div>
                        <div class="form-group">
                            <label for="check_out">Check-out</label>
                            <input type="date" id="check_out" name="check_out" required>
                        </div>
                        <div class="form-group">
                            <label for="guests">Guests</label>
                            <select id="guests" name="guests">
                                <option value="1">1 Guest</option>
                                <option value="2" selected>2 Guests</option>
                                <option value="3">3 Guests</option>
                                <option value="4">4 Guests</option>
                                <option value="5">5+ Guests</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="search-btn">Search Hotels</button>
                </form>
            </div>
        </div>
        
        <div class="features">
            <div class="features-grid">
                <div class="feature">
                    <h3>🏨 Wide Selection</h3>
                    <p>Choose from thousands of hotels, apartments, and unique accommodations worldwide.</p>
                </div>
                <div class="feature">
                    <h3>💰 Best Prices</h3>
                    <p>We guarantee the best prices with our price matching policy and exclusive deals.</p>
                </div>
                <div class="feature">
                    <h3>🔒 Secure Booking</h3>
                    <p>Your booking is protected with our secure payment system and instant confirmation.</p>
                </div>
                <div class="feature">
                    <h3>📞 24/7 Support</h3>
                    <p>Our customer support team is available 24/7 to help with your booking needs.</p>
                </div>
            </div>
        </div>
        
        <div class="cta">
            <h2>Ready to Start Your Journey?</h2>
            <p>Join millions of travelers who trust us with their accommodation needs</p>
            <a href="/public/search" class="cta-btn">Explore Hotels</a>
        </div>
        
        <script>
            // Set default dates
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            document.getElementById('check_in').value = today.toISOString().split('T')[0];
            document.getElementById('check_out').value = tomorrow.toISOString().split('T')[0];
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/search", response_class=HTMLResponse)
def search_results_page(
    city: Optional[str] = Query(None),
    check_in: Optional[date] = Query(None),
    check_out: Optional[date] = Query(None),
    guests: int = Query(2),
    session: Session = Depends(get_session)
):
    """Search results page with server-side rendering for SEO."""
    
    search_service = SearchService(session)
    
    # Get search results
    results = search_service.search_properties(
        city=city,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        limit=20
    )
    
    # Generate HTML for search results
    properties_html = ""
    for prop in results["properties"]:
        min_price = prop.get("min_price", 0)
        properties_html += f"""
        <div class="property-card">
            <div class="property-image">
                <img src="{prop.get('main_image_url', '/static/placeholder.jpg')}" alt="{prop['name']}" />
            </div>
            <div class="property-info">
                <h3><a href="/public/properties/{prop['id']}">{prop['name']}</a></h3>
                <p class="location">{prop.get('city', '')}, {prop.get('country', '')}</p>
                <p class="description">{prop.get('description', '')[:150]}...</p>
                <div class="property-footer">
                    <div class="rating">
                        {'⭐' * (prop.get('star_rating', 0) or 0)}
                    </div>
                    <div class="price">
                        From ${min_price:.2f}/night
                    </div>
                </div>
            </div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hotels in {city or 'All Destinations'} - Hotel Booking System</title>
        <meta name="description" content="Find and book hotels in {city or 'your destination'}. Compare prices and amenities for the perfect stay.">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }}
            .header {{ background: #667eea; color: white; padding: 20px; }}
            .header h1 {{ margin: 0; }}
            .search-summary {{ background: white; padding: 20px; margin: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .results-container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .property-card {{ background: white; margin-bottom: 20px; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; }}
            .property-image {{ width: 300px; height: 200px; }}
            .property-image img {{ width: 100%; height: 100%; object-fit: cover; }}
            .property-info {{ flex: 1; padding: 20px; }}
            .property-info h3 {{ margin: 0 0 10px 0; }}
            .property-info h3 a {{ text-decoration: none; color: #333; }}
            .property-info h3 a:hover {{ color: #667eea; }}
            .location {{ color: #666; margin: 5px 0; }}
            .description {{ color: #888; margin: 10px 0; }}
            .property-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 15px; }}
            .price {{ font-size: 18px; font-weight: bold; color: #667eea; }}
            .no-results {{ text-align: center; padding: 50px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hotel Search Results</h1>
        </div>
        
        <div class="results-container">
            <div class="search-summary">
                <h2>Hotels in {city or 'All Destinations'}</h2>
                <p>
                    {check_in.strftime('%B %d, %Y') if check_in else 'Flexible dates'} - 
                    {check_out.strftime('%B %d, %Y') if check_out else 'Flexible dates'} • 
                    {guests} guest{'s' if guests != 1 else ''}
                </p>
                <p>Found {results['total']} properties</p>
            </div>
            
            <div class="results">
                {properties_html if properties_html else '<div class="no-results"><h3>No properties found</h3><p>Try adjusting your search criteria.</p></div>'}
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/properties/{property_id}", response_class=HTMLResponse)
def property_details_page(
    property_id: uuid.UUID,
    check_in: Optional[date] = Query(None),
    check_out: Optional[date] = Query(None),
    guests: int = Query(2),
    session: Session = Depends(get_session)
):
    """Property details page with server-side rendering for SEO."""
    
    search_service = SearchService(session)
    
    try:
        property_details = search_service.get_property_details(
            property_id=property_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests
        )
    except HTTPException:
        return HTMLResponse(content="<h1>Property not found</h1>", status_code=404)
    
    # Generate room types HTML
    rooms_html = ""
    for room in property_details.get("available_room_types", []):
        rooms_html += f"""
        <div class="room-card">
            <h4>{room['name']}</h4>
            <p>{room.get('description', '')}</p>
            <div class="room-details">
                <span>Max {room['max_occupancy']} guests</span>
                <span>{room['available_count']} available</span>
                <span class="price">${room['price']:.2f} total</span>
            </div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{property_details['name']} - {property_details.get('city', '')} | Hotel Booking</title>
        <meta name="description" content="{property_details.get('description', '')[:160]}">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .header {{ background: #667eea; color: white; padding: 20px; }}
            .property-header {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .property-title {{ font-size: 2.5em; margin: 0; }}
            .property-location {{ font-size: 1.2em; margin: 10px 0; opacity: 0.9; }}
            .property-content {{ max-width: 1200px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }}
            .property-main {{ }}
            .property-sidebar {{ background: #f8f9fa; padding: 20px; border-radius: 10px; }}
            .property-description {{ margin: 20px 0; line-height: 1.6; }}
            .rooms-section {{ margin: 30px 0; }}
            .room-card {{ background: white; padding: 20px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .room-details {{ display: flex; justify-content: space-between; margin-top: 10px; }}
            .price {{ font-weight: bold; color: #667eea; }}
            .booking-widget {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .book-btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="property-header">
                <h1 class="property-title">{property_details['name']}</h1>
                <p class="property-location">
                    {property_details.get('address', '')}, {property_details.get('city', '')}, {property_details.get('country', '')}
                </p>
                <div class="rating">
                    {'⭐' * (property_details.get('star_rating', 0) or 0)}
                </div>
            </div>
        </div>
        
        <div class="property-content">
            <div class="property-main">
                <div class="property-description">
                    <h2>About this property</h2>
                    <p>{property_details.get('description', 'No description available.')}</p>
                </div>
                
                <div class="property-details">
                    <h3>Property Details</h3>
                    <ul>
                        <li>Property Type: {property_details.get('property_type', 'Hotel')}</li>
                        <li>Check-in: {property_details.get('check_in_time', 'N/A')}</li>
                        <li>Check-out: {property_details.get('check_out_time', 'N/A')}</li>
                        <li>Contact: {property_details.get('contact_phone', 'N/A')}</li>
                    </ul>
                </div>
                
                <div class="rooms-section">
                    <h2>Available Rooms</h2>
                    {rooms_html if rooms_html else '<p>No rooms available for selected dates.</p>'}
                </div>
            </div>
            
            <div class="property-sidebar">
                <div class="booking-widget">
                    <h3>Book Your Stay</h3>
                    <p>From ${property_details.get('min_price', 0):.2f}/night</p>
                    <form action="/auth/register" method="get">
                        <input type="hidden" name="property_id" value="{property_id}">
                        <input type="hidden" name="check_in" value="{check_in or ''}">
                        <input type="hidden" name="check_out" value="{check_out or ''}">
                        <input type="hidden" name="guests" value="{guests}">
                        <button type="submit" class="book-btn">Book Now</button>
                    </form>
                    <p style="font-size: 12px; color: #666; margin-top: 10px;">
                        Free cancellation • No booking fees
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/cities")
def get_popular_destinations(
    session: Session = Depends(get_session)
):
    """Get popular destinations for marketing pages."""
    
    # Get cities with property counts
    cities = session.exec(
        select(
            Property.city,
            Property.country,
            func.count(Property.id).label("property_count")
        )
        .where(
            and_(
                Property.is_active == True,
                Property.city.is_not(None),
                Property.city != ""
            )
        )
        .group_by(Property.city, Property.country)
        .order_by(func.count(Property.id).desc())
        .limit(50)
    ).all()
    
    return {
        "destinations": [
            {
                "city": city,
                "country": country,
                "property_count": count,
                "url": f"/public/search?city={city}"
            }
            for city, country, count in cities
        ]
    }


@router.get("/sitemap.xml")
def generate_sitemap(session: Session = Depends(get_session)):
    """Generate XML sitemap for SEO."""
    
    # Get all active properties
    properties = session.exec(
        select(Property).where(Property.is_active == True).limit(1000)
    ).all()
    
    # Get popular cities
    cities = session.exec(
        select(Property.city)
        .where(and_(Property.is_active == True, Property.city.is_not(None)))
        .distinct()
        .limit(100)
    ).all()
    
    urls = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>",
        "<url><loc>https://yourdomain.com/public/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>",
        "<url><loc>https://yourdomain.com/public/search</loc><changefreq>daily</changefreq><priority>0.8</priority></url>"
    ]
    
    # Add property pages
    for prop in properties:
        urls.append(f"<url><loc>https://yourdomain.com/public/properties/{prop.id}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>")
    
    # Add city pages
    for city in cities:
        if city:
            urls.append(f"<url><loc>https://yourdomain.com/public/search?city={city}</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>")
    
    urls.append("</urlset>")
    
    return "\n".join(urls)


@router.get("/robots.txt")
def robots_txt():
    """Generate robots.txt for SEO."""
    
    content = """User-agent: *
Allow: /public/
Allow: /auth/
Disallow: /admin/
Disallow: /api/
Disallow: /organizations/
Disallow: /subscriptions/

Sitemap: https://yourdomain.com/public/sitemap.xml
"""
    
    return content
