import re

import pandas as pd


CATEGORY_RULES = {
    "Kitchen & Dining": (
        r"\b(?:MUG|CUP|PLATE|BOWL|JAR|BOTTLE|GLASS|CUTLERY|SPOON|FORK|KNIFE|"
        r"TEAPOT|TEACUP|SAUCER|TRAY|CAKE|CAKESTAND|BAKING|SNACK|JAM MAKING|TIN|NAPKIN|KITCHEN|TEA|COFFEE|LUNCH|COASTER|"
        r"CHOPPING|DISH|PLACEMAT|PANTRY|JUG|BAKE|BISCUIT|EGG|APRON)\b"
    ),
    "Home Decor": (
        r"\b(?:HEART|CANDLES?|FRAME|CLOCK|LANTERN|LIGHTS?|CUSHION|DOORMAT|MIRROR|"
        r"DECORATION|ORNAMENT|SIGN|CABINET|DRAWER|HANGER|HOOK|RUG|VASE|"
        r"WALL|SHELF|HOLDER|BASKET|PHOTO|PICTURE|CURTAIN|DOOR|FLOWER|BLACK BOARD|MEMOBOARD|BUILDING BLOCK WORD|STORAGE CUBES|CHEST|COAT RACK|WARMER)\b"
    ),
    "Party & Gift Wrap": (
        r"\b(?:GIFT|WRAP|RIBBON|PARTY|BUNTING|BIRTHDAY|CHRISTMAS|XMAS|EASTER|"
        r"HALLOWEEN|CARD|TAG|CRACKER|GARLAND|TINSEL|STOCKING|BAUBLE|BOX|"
        r"PACKING|WEDDING|CONFETTI|TISSUE|CAKE CASES)\b"
    ),
    "Bags & Accessories": (
        r"\b(?:BAG|WALLET|PURSE|NECKLACE|BRACELET|RING|HAIR|SCARF|UMBRELLA|"
        r"KEYRING|KEY RING|CHARM|BROOCH|PENDANT|JEWELLERY|HANDBAG|TOTE|"
        r"EARRING|BELT|LUGGAGE|SHOPPER)\b"
    ),
    "Toys & Stationery": (
        r"\b(?:TOY|DOLL|GAME|PUZZLE|NOTEBOOK|PEN|PENCIL|STICKER|CHALK|SCHOOL|"
        r"ERASER|CRAYON|SKETCH|PAPER|RULER|BOOK|STAMP|PAINT|DESK|MEMO|"
        r"PLAYING CARDS?|SNAP CARDS?|GLIDERS?|JIGSAW)\b"
    ),
    "Garden & Outdoor": (
        r"\b(?:GARDEN|BIRD|PLANT|POTTING|WATERING|PICNIC|OUTDOOR|BEACH|"
        r"PARASOL|HAMMOCK|SEED|HERB|SHED|BIRDHOUSE)\b"
    ),
    "Bath & Personal Care": (
        r"\b(?:BATH|SOAP|TOWEL|TOILET|COSMETIC|MAKEUP|COMB|BRUSH|PERFUME|"
        r"HOT WATER BOTTLE|TISSUES|MANICURE)\b"
    ),
    "Crafts & Sewing": (
        r"\b(?:SEWING|KNITTED|KNITTING|WOOL|YARN|FABRIC|THREAD|BUTTON|BEAD|"
        r"CROCHET|CRAFT|PATCH|FELT)\b"
    ),
}


def add_categories(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    descriptions = result["Description"].fillna("").str.upper()
    result["Category"] = "Other"
    result.loc[descriptions.str.contains(r"\bCAKE CASES\b"), "Category"] = (
        "Party & Gift Wrap"
    )
    for category, pattern in CATEGORY_RULES.items():
        unmatched = result["Category"].eq("Other")
        result.loc[unmatched & descriptions.str.contains(pattern, regex=True), "Category"] = category
    return result


def headline_metrics(frame: pd.DataFrame) -> dict:
    total_revenue = float(frame["Revenue"].sum())
    customer_revenue = (
        frame.dropna(subset=["CustomerID"])
        .groupby("CustomerID", observed=True)["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    uk_revenue = float(
        frame.loc[frame["Country"].eq("United Kingdom"), "Revenue"].sum()
    )
    safe_total = total_revenue or 1.0
    return {
        "rows": int(len(frame)),
        "orders": int(frame["InvoiceNo"].nunique()),
        "customers": int(frame["CustomerID"].nunique()),
        "total_revenue": total_revenue,
        "uk_revenue_share": uk_revenue / safe_total,
        "top_customer_share": (
            float(customer_revenue.iloc[0]) / safe_total if len(customer_revenue) else 0.0
        ),
        "top_10_customer_share": float(customer_revenue.head(10).sum()) / safe_total,
    }


def category_performance(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("Category", observed=True)
        .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
        .assign(revenue_share=lambda value: value["revenue"] / value["revenue"].sum())
        .sort_values("revenue", ascending=False)
        .reset_index()
    )


def customer_performance(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.dropna(subset=["CustomerID"])
        .groupby("CustomerID", observed=True)
        .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
        .sort_values("revenue", ascending=False)
        .reset_index()
    )


def country_performance(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("Country", observed=True)
        .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
        .assign(revenue_share=lambda value: value["revenue"] / value["revenue"].sum())
        .sort_values("revenue", ascending=False)
        .reset_index()
    )


def monthly_performance(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["month"] = result["InvoiceDate"].dt.to_period("M").astype(str)
    return (
        result.groupby("month", observed=True)
        .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
        .assign(average_order_value=lambda value: value["revenue"] / value["orders"])
        .reset_index()
    )
