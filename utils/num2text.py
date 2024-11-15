import streamlit as st
# Function to convert numbers to Arabic words with correct grammar
def number_to_arabic_words(num):
    if num < 0:
        return "عدد سالب غير صالح"  # Invalid negative number
    arabic_numbers = {
        0: "صفر", 1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة",
        5: "خمسة", 6: "ستة", 7: "سبعة", 8: "ثمانية", 9: "تسعة",
        10: "عشرة", 11: "أحد عشر", 12: "اثنا عشر", 20: "عشرون",
        30: "ثلاثون", 40: "أربعون", 50: "خمسون", 60: "ستون",
        70: "سبعون", 80: "ثمانون", 90: "تسعون", 100: "مئة",
        200: "مئتان", 300: "ثلاثمئة", 400: "أربعمئة", 500: "خمسمئة",
        600: "ستمئة", 700: "سبعمئة", 800: "ثمانمئة", 900: "تسعمئة",
        1000: "ألف", 2000: "ألفان", 1000000: "مليون"
    }
    if num in arabic_numbers:
        return arabic_numbers[num]
    parts = []
    if num < 100:
        tens = (num // 10) * 10
        units = num % 10
        if units == 0:
            parts.append(arabic_numbers[tens])
        else:
            parts.append(arabic_numbers[units])
            parts.append("و")
            parts.append(arabic_numbers[tens])
    elif num < 1000:
        hundreds = (num // 100) * 100
        remainder = num % 100
        parts.append(arabic_numbers[hundreds])
        if remainder > 0:
            parts.append("و")
            parts.append(number_to_arabic_words(remainder))
    elif num < 1000000:
        thousands = num // 1000
        remainder = num % 1000
        if thousands == 1:
            parts.append("ألف")
        elif thousands == 2:
            parts.append("ألفان")
        elif 3 <= thousands <= 10:
            parts.append(number_to_arabic_words(thousands))
            parts.append("آلاف")
        else:
            parts.append(number_to_arabic_words(thousands))
            parts.append("ألف")
        
        if remainder > 0:
            parts.append("و")
            parts.append(number_to_arabic_words(remainder))
    elif num == 1000000:
        return "مليون"
    return " ".join(parts)
# Function to format the amount in Libyan Dinar with prefix and suffix, including decimals for milliemes
def format_currency(amount):
    if amount < 0:
        return "عدد سالب غير صالح"  # Invalid negative number
    if amount == 0:
        return "فقط صفر دينار لا غير"
    dinars = int(amount)  # Whole number part in Dinars
    milliemes = int(round((amount - dinars) * 1000))  # Decimal part in milliemes
    parts = []
    # Convert dinars part
    if dinars > 0:
        if dinars == 1:
            parts.append("دينار واحد")
        elif dinars == 2:
            parts.append("ديناران")
        elif 3 <= dinars <= 10:
            parts.append(number_to_arabic_words(dinars))
            parts.append("دنانير")
        else:
            parts.append(number_to_arabic_words(dinars))
            parts.append("دينار")
    # Convert milliemes part
    if milliemes > 0:
        if dinars > 0:
            parts.append("و")  # Add "و" only if dinars part is present
        if milliemes == 1:
            parts.append("مليم واحد")
        elif milliemes == 2:
            parts.append("مليمان")
        elif 3 <= milliemes <= 10:
            parts.append(number_to_arabic_words(milliemes))
            parts.append("ملليمات")
        else:
            parts.append(number_to_arabic_words(milliemes))
            parts.append("مليم")
    # Join the parts with prefix and suffix
    result = "فقط " + " ".join(parts) + " لا غير"
    return result
# Streamlit UI
st.title("تحويل الأرقام إلى كلمات عربية - الدينار الليبي")
# Input from user
user_input = st.text_input("أدخل المبلغ (بالدينار، على سبيل المثال: 1500.250):")
# Validate input
if user_input:
    try:
        amount = float(user_input)  # Accept decimal input
        if amount >= 0:
            arabic_words = format_currency(amount)  # Treat the input as Dinars
            st.success(f"المبلغ {amount} يُكتب كـ: {arabic_words}")
        else:
            st.error("يرجى إدخال مبلغ غير سالب.")
    except ValueError:
        st.error("يرجى إدخال رقم صحيح.")
class Num2Word_AR:
    def __init__(self):
        self.high_numwords = ["", "ألف", "مليون", "مليار", "بليون", "كوادريليون", "كوينتليون"]
        self.mid_numwords = [(100, "مائة", "مائتان", "مئات"),
                             (10, "عشرة", "عشرون", "عشرات"),
                             (1, "واحد", "إثنان", "")]
        self.errmsg_nonnum = "المدخلات يجب ان تكون رقمية فقط."
        self.cards = ["صفر", "واحد", "إثنان", "ثلاثة", "أربعة", "خمسة",
                      "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
                      "إحدى عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر",
                      "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
        
    def to_cardinal(self, value):
        if not isinstance(value, int):
            return self.errmsg_nonnum
        
        if value < 20:
            return self.cards[value]
        
        words = []
        for scale, inc in enumerate(self.high_numwords):
            if value == 0:
                break
            value, rnum = divmod(value, 1000)
            if rnum > 0:
                words.append(self.merge(rnum) + " " + self.high_numwords[scale])
        return " و ".join(reversed(words)).strip()
    
    def merge(self, value):
        words = []
        for scale, forms in self.mid_numwords:
            lnum, rnum = divmod(value, scale)
            if lnum == 0:
                continue
            if lnum == 1:
                word = forms[1]
            elif lnum == 2:
                word = forms[2]
            else:
                word = self.cards[lnum] + " " + forms[3]
            words.append(word)
            value = rnum
        return " و ".join(words)
    
    def to_ordinal(self, value):
        # Example of ordinal conversion
        cardinal = self.to_cardinal(value)
        if cardinal == "واحد":
            return "الأول"
        elif cardinal == "إثنان":
            return "الثاني"
        # This example is simplified; expand as needed
        return f"{cardinal}th"
    
    def to_ordinal_num(self, value):
        return f"{value}."
    def to_currency(self, val, currency="دينار", cents="درهم"):
        dinars, dirhams = divmod(val, 100)
        parts = []
        if dinars:
            parts.append(self.to_cardinal(dinars) + " " + currency)
        if dirhams:
            parts.append(self.to_cardinal(dirhams) + " " + cents)
        return " و ".join(parts)
# Example usage and testing
def main():
    converter = Num2Word_AR()
    print("Cardinal:", converter.to_cardinal(1234))
    print("Ordinal:", converter.to_ordinal(1))
    print("Ordinal Number:", converter.to_ordinal_num(2))
    print("Currency:", converter.to_currency(12345))
if __name__ == "__main__":
    main()
