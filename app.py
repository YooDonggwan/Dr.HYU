from flask import Flask, render_template, request, redirect
from apicall import hosp_list, pharm_list
import apicall
import pprint

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# @app.route('/')
# def index():            
#     return render_template("index.html")

@app.route('/')
def index():
    check = apicall.create_table("hosp_table") # 테이블 생성 되었는지 체크
    if check is False:
        apicall.input_csv() # 멤버 정보 csv삽입
        apicall.init_hosp_table() # 병원 초기 DB
        apicall.init_pharm_table() # 약국 초기 DB
        apicall.insert_glasses() # 안경원 DB
    result = apicall.member_list()
    return render_template("main.html", members = result)



###### 로그인, 회원가입 #######
@app.route('/login', methods=['GET', 'POST'])
def login():
    local = request.form.get("local")
    domain = request.form.get("domain")
    passwd = request.form.get("passwd")
    result = apicall.select_id_cnt("member", local, domain, passwd)
    print(result)
    if result > 1:
        return render_template("select_usertype.html")
    elif result == 1:
        result = apicall.search_usertype("member", local, domain, passwd)
        print(result)
        if result == None:
            return render_template("input_usertype.html")
        elif result == "병원":
            visitor = apicall.search_visitor("병원")
            reserve = apicall.search_every_reserve()
            return render_template("hosp.html", reserve = reserve, visitor = visitor)
        elif result == "환자":
            name = apicall.search_name(local, domain, passwd)
            check = apicall.search_check_presc(name)
            return render_template("patient.html", check = check)
        elif result == "약국":
            visitor = apicall.search_visitor("약국")
            return render_template("pharm.html", visitor = visitor)
        # 로그인완료 경고창 띄우면서 넘어가기
        # return render_template("service.html")
    elif result == 0:
        return "회원정보가 존재하지 않습니다. 회원가입을 해주세요"
    ## 만약에 로그인정보가 없으면 로그인정보가 없다고 경고창 띄우고 회원가입으로 이동시키거나 다시 로그인하라고 해야함

@app.route('/go-hosppg', methods=['POST'])
def go_hosppg():
    return render_template("hosp.html")

@app.route('/go-patientpg', methods=['POST'])
def go_patientpg():
    return render_template("patient.html")

@app.route('/go-pharmpg', methods=['POST'])
def go_pharmpg():
    return render_template("pharm.html")

@app.route('/call-join', methods=['POST'])
def call_join():
    return render_template("join.html")

@app.route('/join', methods=['POST'])
def join():
    local = request.form.get("local")
    domain = request.form.get("domain")
    passwd = request.form.get("passwd")
    result1 = apicall.select_id_cnt("member", local, domain, passwd)
    result2 = apicall.search_usertype("member", local, domain, passwd)
    if result1 > 0 and result2 == []:
        return render_template("input_usertype.html")
    usertype = request.form.get("usertype")

    apicall.insert_member("memeber", local, domain, passwd, usertype)

    return "회원가입이 완료되었습니다!"
    
@app.route('/input_usertype', methods=['POST'])
def input_usertype():
    local = request.form.get("local")
    domain = request.form.get("domain")
    passwd = request.form.get("passwd")
    usertype = request.form.get("usertype")
    apicall.insert_usertype("member", local, domain, passwd, usertype)

    return render_template("main.html")




####### 병원 #######

# 내 병원페이지 가기
@app.route('/gomyhosp', methods=["POST"])
def gomyhosp():
    my_hosp = request.form.get("hosp_name")
    hosp = apicall.search_my_hosp(my_hosp)
    reservelist = apicall.search_reserve_list(my_hosp)

    return render_template("myhosp.html", hosp = hosp, reservelist = reservelist)


@app.route('/del-reserve', methods=["POST"])
def del_reserve():
    name = request.form.get("name")
    phone = request.form.get("phone")

    apicall.delete_reservation(name, phone)

    return render_template("hosp.html")


# 처방전 생성 페이지로 이동
@app.route('/go-prescribe', methods=['POST'])
def go_prescribe():
    return render_template("prescribe.html")

# 처방전 만들기
@app.route('/make-prescribe', methods=['POST'])
def make_prescribe():
    code = request.form.get('code')
    presc_day = request.form.get('presc_day')
    patient_name = request.form.get('patient_name')
    hosp_name = "한양대병원"
    medicine = request.form.get('medicine')
    dose = request.form.get('dose')
    num_dose = request.form.get('num_dose')
    total_day = request.form.get('total_day')

    #병원입장에서 입력하는 것들만 일단 넣어줌
    apicall.insert_prescription_hosp(code, presc_day, patient_name, hosp_name, medicine, dose, num_dose, total_day)

    return render_template("hosp.html")

# 처방전 검색
@app.route('/search-prescription', methods=['POST'])
def search_person_prescription():
    patient_name = request.form.get('patient_name')
    code = request.form.get('code')
    presc_day = request.form.get('presc_day')

    result = apicall.search_person_prescription(patient_name, code, presc_day)

    print(result)

    return render_template("prescription_hosp.html", hosp = result)
    ##처방기록 화면에 표시해주어야함

####### 환자 #######

@app.route('/favor-hosp', methods=['POST'])
def favor_hosp():
    # 자주가는 병원 등록
    name = request.form.get("name")
    phone = request.form.get("phone")
    hname = request.form.get("hname")
    usertype = "환자"

    apicall.insert_favor_hosp("member", name, phone, usertype, hname)

    return render_template("patient.html")

@app.route('/recently-hosp', methods=['POST'])
def recently_hosp():
    #최근 방문한 병원
    patient_name = request.form.get("patient_name")
    phone = request.form.get("phone")
    usertype = "환자"

    result = apicall.search_recently_hosp(patient_name, phone, usertype)

    return render_template("recently_visit.html", hosp = result)

@app.route('/search-hosp', methods=['POST'])
def search_hosp():
    patient_name = request.form.get("patient_name")
    phone = request.form.get("phone")
    usertype = "환자"

    lat = apicall.search_user_location_lat(patient_name, phone, usertype)
    if lat == None:
        lat = 37.5585146
    lng = apicall.search_user_location_lng(patient_name, phone, usertype)
    if lng == None:
        lat = 127.0331892

    apicall.update_hosp_table(lat,lng) # 주변 병원 추가

    # 주변 병원 이름 찾아오기
    hosp_name = apicall.search_hosp_name() # 모든 병원들의 이름이 들어감
    # 병원 위치 가져오기 
    hosp_location = apicall.search_hosp_location()

    hosp_info = apicall.search_hosp_information()

    return render_template("map_hosp.html", lat = lat, lng = lng, hosp_name = hosp_name, 
                            loca = hosp_location, info = hosp_info)

@app.route('/search-pharm', methods=['POST'])
def search_pharm():
    patient_name = request.form.get("patient_name")
    phone = request.form.get("phone")
    usertype = "환자"

    lat = apicall.search_user_location_lat(patient_name, phone, usertype)
    if lat == None:
        lat = 37.5585146
    lng = apicall.search_user_location_lng(patient_name, phone, usertype)
    if lng == None:
        lat = 127.0331892

    apicall.update_pharm_table(lat,lng) # 주변 약국 추가

    pharm_name = apicall.search_pharm_name() # 모든 약국들 이름 찾기
    # 약국들 위치 가져오기 
    pharm_location = apicall.search_pharm_location()

    pharm_info = apicall.search_pharm_information()

    return render_template("map_pharm.html", lat = lat, lng = lng, pharm_name = pharm_name, ploca = pharm_location, pinfo = pharm_info)


@app.route('/visit-hosp', methods=["POST"]) # 병원 방문하기
def visit_hosp():
    name = request.form.get("name")
    phone = request.form.get("phone")
    hname = request.form.get("hname")
    usertype = "환자"
    placetype = "병원"
    #방문을 하면 멤버 테이블에 최근 방문 병원 바꾸고
    apicall.change_recently("member", name, phone, usertype, hname)
    #방문 테이블에 방문이력 만들기
    apicall.insert_place_visit(placetype, hname, name, phone)

    return render_template("patient.html")

@app.route('/visit-pharm', methods=["POST"]) # 병원 방문하기
def visit_pharm():
    name = request.form.get("name")
    phone = request.form.get("phone")
    hname = request.form.get("hname")
    usertype = "환자"
    placetype = "약국"
    #방문을 하면 멤버 테이블에 최근 방문 병원 바꾸고
    apicall.change_recently("member", name, phone, usertype, hname)
    #방문 테이블에 방문이력 만들기
    apicall.insert_place_visit(placetype, hname, name, phone)

    return render_template("patient.html")

@app.route('/reserve-hosp', methods=["POST"]) # 병원 예약하기
def reserve_hosp():
    place_type = "병원"
    place_name = request.form.get("hname")
    p_name = request.form.get("name")
    p_phone = request.form.get("phone")
    p_reserveday = request.form.get("day")
    p_reservetime = request.form.get("time")

    apicall.insert_place_reserve(place_type, place_name, p_name, p_phone, p_reserveday, p_reservetime)

    return render_template("patient.html")

@app.route('/reserve-pharm', methods=["POST"])
def reserve_pharm():
    place_type = "약국"
    place_name = request.form.get("hname")
    p_name = request.form.get("name")
    p_phone = request.form.get("phone")
    p_reserveday = request.form.get("day")
    p_reservetime = request.form.get("time")

    apicall.insert_place_reserve(place_type, place_name, p_name, p_phone, p_reserveday, p_reservetime)

    return render_template("patient.html")


###### 약국 ########
@app.route('/pharm-reserve', methods=["POST"])
def pharm_reserve():
    name = request.form.get("name")
    placetype = "약국"
    placename = request.form.get("placename")
    
    result = apicall.search_pharm_reserve(placetype, placename, name)
    if result != None:
        prescription = apicall.search_prescription_pharm(name)
        return render_template("prescription_pharm.html", prescription = prescription)
    
    return render_template("pharm.html")

@app.route('/yes-prescribe', methods=["POST"])
def yes_prescribe():
    name = request.form.get("name")
    apicall.update_prescription_check(name, "Yes")
    return render_template("pharm_prescribe.html")

@app.route('/no-prescribe', methods=["POST"])
def no_prescribe():
    #약국 처방 가능여부 넣기
    name = request.form.get("name")
    apicall.update_prescription_check(name, "No")
    return render_template("pharm.html")

@app.route('/make-medicine', methods=["POST"])
def make_medicine():
    prescribe_check = "Yes"
    name = request.form.get("name")
    pharm_name = "한양대약국"
    make_day = request.form.get("make_day")
    comment = request.form.get("comment")
    apicall.update_prescription_pharm(name, pharm_name, make_day, comment, prescribe_check)
    return render_template("pharm.html")

@app.route('/check-presc', methods=["POST"])
def check_presc():
    return render_template("patient.html")

### 안경원 ###

@app.route('/glasses-list', methods=["POST"])
def glasses_list():

    glasses = apicall.search_glasses_info()
    return render_template("glasses.html", glasses = glasses)

#### 뒤로가기 ####

@app.route('/backpatient', methods=["POST"])
def backpatient():
    return render_template("patient.html")

@app.route('/backhosp', methods=["POST"])
def backhosp():
    return render_template("hosp.html")

@app.route('/backpharm', methods=["POST"])
def backpharm():
    return render_template("pharm.html")

@app.route('/logout', methods=["POST"])
def logout():
    return render_template("main.html")


if __name__ == ("__main__"):
    app.run(debug=True, host='0.0.0.0', port=5030)