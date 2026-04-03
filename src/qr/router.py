from fastapi import APIRouter, Response
import qrcode
import io

router = APIRouter(prefix="/qr", tags=["qr"])

@router.get("/merchant/{vpa}")
async def generate_merchant_qr(
    vpa: str,
    amount_paise: int | None = None
) -> Response:
    """
    Generates a generic URI string embedded inside a PNG file representing standard
    Unified Payments Interface configurations for PayFast compatible targets.
    """
    url = f"upi://pay?pa={vpa}&pn=PayFastUser"
    if amount_paise and amount_paise > 0:
        url += f"&am={amount_paise / 100:.2f}"
        
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return Response(content=img_byte_arr, media_type="image/png")
