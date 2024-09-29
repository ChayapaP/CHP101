from flask import Flask, request, render_template

app = Flask(__name__)

def calculate_waste_and_sheets(original_width, original_height, desired_width, desired_height, quantity):
    if desired_width <= 0 or desired_height <= 0:
        return 0, 0  # Return 0 for sheets needed and waste area

    sheets_per_original = (original_width // desired_width) * (original_height // desired_height)
    
    if sheets_per_original == 0:  # If the original paper can't cut this size
        return 0, 0

    sheets_needed = (quantity + sheets_per_original - 1) // sheets_per_original
    
    total_area_used = sheets_needed * original_width * original_height
    total_area_needed = quantity * desired_width * desired_height
    waste_area = total_area_used - total_area_needed

    return sheets_needed, waste_area

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = ""
    alert_message = ""
    results = []
    total_waste = 0  # Total waste area
    total_sheets_needed = 0  # Total sheets needed
    size_widths = [None] * 5  # List for width sizes
    size_heights = [None] * 5  # List for height sizes
    quantities = [None] * 5  # List for quantities
    original_size = None  # To keep track of original size input
    custom_width = None  # Custom width input
    custom_height = None  # Custom height input

    if request.method == 'POST':
        original_size = request.form.get('original_size', None)
        custom_width = request.form.get('custom_width', '')
        custom_height = request.form.get('custom_height', '')

        # Ensure at least one size is entered
        if not original_size and (not custom_width or not custom_height):
            error_message = "กรุณาเลือกขนาดกระดาษต้นฉบับหรือใส่ขนาดกระดาษเอง"
            return render_template('index.html', error_message=error_message,
                                   size_widths=size_widths, size_heights=size_heights, quantities=quantities,
                                   original_size=original_size, custom_width=custom_width, custom_height=custom_height)

        if original_size:
            try:
                original_width, original_height = map(int, original_size.split('x'))
            except ValueError:
                error_message = "เกิดข้อผิดพลาด: กรุณาเลือกขนาดกระดาษต้นฉบับที่ถูกต้อง"
                return render_template('index.html', error_message=error_message,
                                       size_widths=size_widths, size_heights=size_heights, quantities=quantities,
                                       original_size=original_size, custom_width=custom_width, custom_height=custom_height)
        else:
            try:
                original_width = int(custom_width)
                original_height = int(custom_height)
            except ValueError:
                error_message = "เกิดข้อผิดพลาด: กรุณาใส่ขนาดกระดาษต้นฉบับที่ถูกต้อง"
                return render_template('index.html', error_message=error_message,
                                       size_widths=size_widths, size_heights=size_heights, quantities=quantities,
                                       original_size=original_size, custom_width=custom_width, custom_height=custom_height)

        for i in range(1, 6):
            width = request.form.get(f'size_width_{i}', '')
            height = request.form.get(f'size_height_{i}', '')
            quantity = request.form.get(f'quantity_{i}', '')

            # Save user input
            size_widths[i-1] = width if width else None
            size_heights[i-1] = height if height else None
            quantities[i-1] = quantity if quantity else None

            if width and height and quantity:
                try:
                    width = int(width)
                    height = int(height)
                    quantity = int(quantity)

                    # Ensure sizes are not zero
                    if width <= 0 or height <= 0 or quantity <= 0:
                        error_message = f"เกิดข้อผิดพลาดที่ขนาดที่ {i}: ขนาดต้องไม่เป็นศูนย์"
                        continue

                    sheets, waste = calculate_waste_and_sheets(
                        original_width, original_height, width, height, quantity
                    )

                    sheets_per_original = (original_width // width) * (original_height // height)

                    results.append({
                        "size": f"{width} mm x {height} mm",
                        "sheets_needed": sheets,
                        "waste": waste / 1_000_000,  # Convert to square meters
                        "sheets_per_original": sheets_per_original,
                    })

                    total_waste += waste  # Add to total waste
                    total_sheets_needed += sheets  # Add to total sheets needed

                except ValueError:
                    error_message = f"เกิดข้อผิดพลาดที่ขนาดที่ {i}: กรุณาใส่ค่าที่ถูกต้อง"
                    continue

        # Check if total waste exceeds 150 square meters
        if total_waste > 150_000_000:  # 150 square meters = 150,000,000 mm²
            alert_message = "คำเตือน: เศษกระดาษรวมทั้งหมดเกิน 150 ตารางเมตร"

    return render_template('index.html', results=results, error_message=error_message, 
                           alert_message=alert_message, total_sheets_needed=total_sheets_needed, 
                           total_waste=total_waste / 1_000_000,  # Convert to square meters for display
                           size_widths=size_widths, size_heights=size_heights, quantities=quantities,
                           original_size=original_size, custom_width=custom_width, custom_height=custom_height)

if __name__ == "__main__":
    app.run(debug=True)