import requests
import json
from supabase import create_client, Client

# ==========================================
# 1. 내 수파베이스 창고 열쇠
# ==========================================
SUPABASE_URL = "https://lhgbenqlcmbvagpcpjja.supabase.co"
SUPABASE_KEY = "sb_publishable_gKGhOGLFzrY4FmVDBIms4g_O0s9VErm"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 공공데이터포털 허가증 및 주소
# ==========================================
BUSAN_API_KEY = "620e72bf67c9551c485b286993097ce9bada862a14062f97d135c7c166b160e5"
API_URL = "http://apis.data.go.kr/6260000/BusanCrsTrnngInfoService/getCrsTrnngInfo"

def fetch_and_update_busan_data():
    print("🔄 진짜 부산시 공공데이터 서버에 접속을 시도합니다...")
    params = {
        'serviceKey': BUSAN_API_KEY,
        'pageNo': '1',
        'numOfRows': '100',
        'resultType': 'json'
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = data['response']['body']['items']['item']
        print(f"✅ 총 {len(items)}개의 진짜 데이터를 찾았습니다! 창고에 넣을게요.")
        
        # ==========================================
        # 3. 완벽한 이름표 짝짓기 (번역기 작동!)
        # ==========================================
        for item in items:
            # 수강료가 '0'이면 '무료', 아니면 '0000원'으로 예쁘게 바꿔주는 마법
            fee_amount = item.get('lctreChargeAmount', '0')
            fee_text = "무료" if fee_amount == "0" else f"{fee_amount}원"

            new_course = {
                "title": item.get('lctreNm', '제목없음'), 
                "facility_name": item.get('resveGroupNm', '장소미상'),
                "latitude": float(item.get('adresLa', 35.1795)), 
                "longitude": float(item.get('adresLo', 129.0756)), 
                "fee": fee_text,
                "status": item.get('progrsSttusNm', '상태미상')
            }
            
            # 수파베이스에 넣기
            supabase.table("busan_courses").insert(new_course).execute()
            
        print("🎉 진짜 데이터 연동이 완벽하게 끝났습니다! 지도를 새로고침 해보세요.")
        
    except Exception as e:
        print(f"❌ 데이터를 가져오는데 문제가 생겼습니다: {e}")

if __name__ == "__main__":
    
    # [선택사항] 새 데이터를 넣기 전에 기존에 잘못 들어간 '제목없음' 데이터들을
    # 싹 지워주고 싶다면 아래 두 줄의 제일 앞 '#' 기호를 지워주세요.
    # print("🧹 기존 데이터를 청소합니다...")
    # supabase.table("busan_courses").delete().neq("id", 0).execute()
    
    fetch_and_update_busan_data()