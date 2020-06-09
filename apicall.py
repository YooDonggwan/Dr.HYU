import json
import requests
import psycopg2 as pg
import psycopg2.extras
from pprint import pprint

pg_local = {
    'host': "127.0.0.1", # localhost
    'user': "postgres",  # dbuser
    'dbname': "postgres",  # dbapp
    'password': "0510"     # password
}

db_connector = pg_local # local로 연결

connect_string = "host={host} user={user} dbname={dbname} password={password}".format(
    **db_connector)

def create_table(table_name):
    
    # table이 이미 존재하는지 체크하기 위한 sql문
    check_sql = f'''SELECT EXISTS(
        SELECT relname
        FROM pg_class
        WHERE relname = ('{table_name}'));
        '''
    # table 생성
    h_sql = f'''CREATE TABLE hosp_table(
                  hosp_name varchar(50),
                  doctor varchar(20),
                  medical_subject varchar(20),
                  addr varchar(50),
                  lng varchar(20),
                  lat varchar(20),
                  distance varchar(50),
                  week_time varchar(10),
                  weekend_time varchar(10)
                );
              '''
    member_sql = f'''CREATE TABLE member (
                name varchar(30),
                phone varchar(20),
                local varchar(20),
                domain varchar(20),
                passwd varchar(20),
                payment varchar(500),
                lat varchar(20),
                lng varchar(20)
              );
           '''
    patientreserve_sql = f'''CREATE TABLE patientreserve_table(
                  place_type varchar(10),
                  place_name varchar(50),
                  p_name varchar(20),
                  p_phone varchar(20),
                  p_reserveday varchar(20),
                  p_reservetime varchar(20)
                );
             '''
    patient_sql = f'''CREATE TABLE patient_table(
                        patient_name varchar(20),
                        patient_phone varchar(20),
                        recently_hosp varchar(50)    
                    );
                   '''
                   
    pharm_sql = f'''CREATE TABLE pharm_table(
                      pharm_name varchar(20),
                      addr varchar(50),
                      lng varchar(20),
                      lat varchar(20),
                      distance varchar(50),
                      week_time varchar(10),
                      weekend_time varchar(10),
                      prescription boolean
                    );
                 '''
    visit_sql = f'''CREATE TABLE place_visit(
                      placetype varchar(30),
                      place_name varchar(50),
                      visitor_name varchar(30),
                      visitor_phone varchar(30)
                      );
                  '''
    prescription_sql = f'''CREATE TABLE prescription(
                            code varchar(20),
                            presc_day varchar(20),
                            patient_name varchar(20),
                            hosp_name varchar(50),
                            medicine varchar(20),
                            dose varchar(10),
                            num_dose varchar(10),
                            total_day varchar(10),
                            pharm_name varchar(50),
                            make_day varchar(10),
                            comment varchar(50),
                            prescribe_check varchar(10)
                          );
                        '''
    glasses_sql = f'''CREATE TABLE glasses(
                        name varchar(50),
                        addr varchar(50),
                        phone varchar(30),
                        open_time varchar(10)
                      );
                   '''
    
    nikon_sql = f'''CREATE TABLE nikon(
                      store_name varchar(50),
                      addr varchar(30),
                      iseeshop varchar(20),
                      leclub varchar(20)
                    );
                 '''

    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(check_sql) # 테이블 검사먼저 실행
        check = cur.fetchone()[0] # 반환받기
        if check is False: # 테이블이 없으면
            cur.execute(h_sql)
            cur.execute(member_sql) # sql 문을 실행
            cur.execute(patientreserve_sql)
            cur.execute(patient_sql)
            cur.execute(pharm_sql)
            cur.execute(visit_sql)
            cur.execute(prescription_sql)
            cur.execute(glasses_sql)
            cur.execute(nikon_sql)
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()
        return check
        
    except pg.OperationalError as e:
        print(e)



def input_csv():
    # csv 파일을 테이블에 업로드하기 위한 함수
    # sql문의 COPY를 통해 테이블에 csv파일을 ','기준으로 나누어 2개의 컬럼으로 업로드 해줌 
    sql = """COPY member FROM STDIN DELIMITER ',' QUOTE '"' HEADER CSV;
          """
    d_sql = f'''ALTER TABLE member
                DROP COLUMN payment;
             '''
    a_sql = f'''ALTER TABLE member
                ADD COLUMN usertype varchar(10) DEFAULT NULL;
             '''
    # 유저타입 컬럼 추가
    ad_sql = f'''ALTER TABLE member
                 ADD COLUMN favor_hosp varchar(50) DEFAULT NULL;
              '''
    # 자주가는 병원 컬럼 추가
    add_sql = f'''ALTER TABLE member
                  ADD COLUMN recently_hosp varchar(50) DEFAULT NULL;
               '''
    # 최근 방문한 병원 컬럼 추가
    with pg.connect(connect_string) as conn:
        with conn.cursor() as cur:
            with open('/Users/YooDongGwan/Desktop/2019_ITE2038_2015004766/DB_Termproject_유동관/customers.csv', 'r') as f:
                # csv파일의 절대경로를 입력받아 csv파일을 오픈 
                cur.copy_expert(sql, f) # 오픈된 파일을 복사하고
                cur.execute(d_sql)
                cur.execute(a_sql)
                cur.execute(ad_sql)
                cur.execute(add_sql)
    conn.commit() # DB에 저장해줌
    conn.close()

def member_list():
    # 테이블을 이용해 html을 만들어줌
    sql = f"""SELECT name,phone,local,domain,passwd,lat,lng, usertype FROM member
    """
    # 테이블 전체 선택
    try:
        conn = pg.connect(connect_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql) # sql실행
        result = cur.fetchall() # 반환시키기 위해 가져옴
        conn.close()
        return result
    except Exception as e:
        print(e),
        return []

def check_member(table_name, local, domain, passwd):
    sql = f"""SELECT local, domain, passwd
              FROM {table_name}
              WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}')
           """
    # 검색하려고 입력한 글자부터 시작되는 모든 연락처를 검색하게 됨
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall() # 실행 결과 가져옴
        conn.close()
        return result # 검색된 행을 리턴

    except pg.OperationalError as e:
        print(e)
        return 0


def insert_member(table_name, local, domain, passwd, usertype):
    sql = f"""INSERT INTO {table_name}
              VALUES ('{local}', '{domain}', '{passwd}', '{usertype}');
           """
    # 테이블에 이름과 번호를 한 행으로 추가 
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def insert_usertype(table_name, local, domain, passwd, usertype):
    sql = f'''UPDATE {table_name} 
              SET usertype = ('{usertype}')
              WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}');
           '''
    # 테이블에 이름과 번호를 한 행으로 추가 
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def insert_new_location_hosp(lat, lng):
    table = hosp_list(lat, lng) # 새로운 위치 받아오기 
    info = table['response']['body']['items']['item']
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      for data in info:
            hosp_name = data['yadmNm']
            doctor = data['sdrCnt']
            medical_subject = "종합진료"
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-18시'
            weekend_time = '10시-16시'
            sql = f'''INSERT INTO hosp_table(hosp_name, doctor, medical_subject, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{hosp_name}\', \'{doctor}\', \'{medical_subject}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\', \'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
      print(e)
      return -1
    return 0

def insert_new_location_pharm(lat, lng):
    table = pharm_list(lat, lng) # 초기 DB는 한양대 주변 5KM
    info = table['response']['body']['items']['item']
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      for data in info:
            pharm_name = data['yadmNm']
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-18시'
            weekend_time = '10시-16시'
            sql = f'''INSERT INTO pharm_table(pharm_name, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{pharm_name}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\',\'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def insert_prescription_hosp(code, presc_day, patient_name, hosp_name, medicine, dose, num_dose, total_day):
    sql = f'''INSERT INTO prescription(code, presc_day, patient_name, hosp_name, medicine, dose, num_dose, total_day)
              VALUES ('{code}', '{presc_day}', '{patient_name}', '{hosp_name}', '{medicine}', 
                        '{dose}', '{num_dose}', '{total_day}');
            '''
    try:
      conn = pg.connect(connect_string) # DB연결(로그인)
      cur = conn.cursor() # DB 작업할 지시자 정하기
      cur.execute(sql) # sql 문을 실행
      # DB에 저장하고 마무리
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
      print(e)
      return -1
    return 0

def insert_place_visit(placetype, place_name, name, phone):
    sql = f'''INSERT INTO place_visit
              VALUES ('{placetype}', '{place_name}', '{name}', '{phone}');
           '''
    try:
      conn = pg.connect(connect_string) # DB연결(로그인)
      cur = conn.cursor() # DB 작업할 지시자 정하기
      cur.execute(sql) # sql 문을 실행
      # DB에 저장하고 마무리
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
      print(e)
      return -1
    return 0

def insert_place_reserve(place_type, place_name, p_name, p_phone, p_reserveday, p_reservetime):
  sql = f'''INSERT INTO patientreserve_table
            VALUES ('{place_type}', '{place_name}', '{p_name}', '{p_phone}', '{p_reserveday}', '{p_reservetime}');
         '''
  try:
    conn = pg.connect(connect_string) # DB연결(로그인)
    cur = conn.cursor() # DB 작업할 지시자 정하기
    cur.execute(sql) # sql 문을 실행
    # DB에 저장하고 마무리
    conn.commit()
    conn.close()
  except pg.OperationalError as e:
    print(e)
    return -1
  return 0

def delete_reservation(name, phone):
    # 삭제함수
    sql = f'''DELETE FROM patientreserve_table
              WHERE p_name = ('{name}') AND p_phone = ('{phone}');
           '''
    # 테이블에서 삭제하려고 입력한 이름과 완전히 일치하는 것만 삭제가 되며 중복된 것이 있을 경우 1개만 삭제
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def search_name(local, domain, passwd):
    sql = f"""SELECT name
              FROM member
              WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}')
           """
    # 검색하려고 입력한 글자부터 시작되는 모든 연락처를 검색하게 됨
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0] # 실행 결과 가져옴
        conn.close()
        return result # 검색된 행을 리턴

    except pg.OperationalError as e:
        print(e)
        return 0

def search_visitor(placetype):
    sql = f"""SELECT place_name, visitor_name, visitor_phone
              FROM place_visit
              WHERE placetype = ('{placetype}');
           """
    # 검색하려고 입력한 글자부터 시작되는 모든 연락처를 검색하게 됨
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall() # 실행 결과 가져옴
        conn.close()
        return result # 검색된 행을 리턴

    except pg.OperationalError as e:
        print(e)
        return 0

def select_id_cnt(table_name, local, domain, passwd):
    # 검색함수
    sql = f""" SELECT COUNT(*) as cnt
               FROM {table_name}
               WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}');
           """
    # 같은 로그인 정보 갯수 세기
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0] # 실행 결과 가져옴
        conn.close()
        return result # 검색된 행을 리턴

    except pg.OperationalError as e:
        print(e)
        return 0

def search_usertype(table_name, local, domain, passwd):
    # 검색함수
    sql = f""" SELECT usertype
               FROM {table_name}
               WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}');
           """
    # 유저타입 찾기
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0] # 실행 결과 가져옴
        conn.close()
        return result # 검색된 행을 리턴

    except pg.OperationalError as e:
        print(e)
        return 0

def search_user_location_lat(patient_name, phone, usertype):
      sql = f'''SELECT lat
                FROM member
                WHERE name = ('{patient_name}') AND phone = ('{phone}') AND usertype = ('{usertype}');
             '''
      # 유저의 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0] # lat 가져오기
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_user_location_lng(patient_name, phone, usertype):
      sql = f'''SELECT lng
                FROM member
                WHERE name = ('{patient_name}') AND phone = ('{phone}') AND usertype = ('{usertype}');
             '''
      # 유저의 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0]  # lng 가져오기
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_recently_hosp(patient_name, phone, usertype):
      sql = f'''SELECT recently_hosp
                FROM member
                WHERE name = ('{patient_name}') AND phone = ('{phone}') AND usertype = ('{usertype}');
             '''
      # 유저의 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchone()[0]
        conn.close()
        return result

      except pg.OperationalError as e:
        print(e)
        return 0


def search_person_prescription(patient_name, code, presc_day):
      sql = f'''SELECT code, presc_day, patient_name, hosp_name, medicine, dose, num_dose, total_day
                FROM prescription
                WHERE patient_name = ('{patient_name}') AND code = ('{code}') AND presc_day = ('{presc_day}');
             '''
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        print(result) ##
        return result # 검색된 행을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_prescription_pharm(patient_name):
      sql = f'''SELECT code, presc_day, patient_name, hosp_name, medicine, dose, num_dose, total_day
                FROM prescription
                WHERE patient_name = ('{patient_name}')
             '''
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 행을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_hosp_location():
      sql = f'''SELECT lat, lng
                FROM hosp_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0


def search_pharm_location():
      sql = f'''SELECT lat, lng
                FROM pharm_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_hosp_name():
      sql = f'''SELECT hosp_name
                FROM hosp_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_pharm_name():
      sql = f'''SELECT pharm_name
                FROM pharm_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_my_hosp(hosp_name):
      sql = f'''SELECT hosp_name, doctor, medical_subject, addr, lat, lng, week_time, weekend_time
                FROM hosp_table
                WHERE hosp_name = ('{hosp_name}')
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_hosp_information():
      sql = f'''SELECT hosp_name, medical_subject, week_time, weekend_time, addr, distance
                FROM hosp_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_pharm_information():
      sql = f'''SELECT pharm_name, week_time, weekend_time, addr, distance
                FROM pharm_table
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_reserve_list(hosp_name):
      sql = f'''SELECT place_name, p_name, p_phone, p_reserveday, p_reservetime
                FROM patientreserve_table
                WHERE place_name = ('{hosp_name}')
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_every_reserve():
      sql = f'''SELECT place_name, p_name, p_phone, p_reserveday, p_reservetime
                FROM patientreserve_table
                WHERE place_type = ('{"병원"}')
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_pharm_reserve(placetype, placename, name):
      sql = f'''SELECT p_reserveday
                FROM patientreserve_table
                WHERE place_type = ('{placetype}') AND place_name = ('{placename}') AND p_name = ('{name}');
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0

def search_check_presc(name):
      sql = f'''SELECT prescribe_check
                FROM prescription
                WHERE patient_name = ('{name}');
             '''
      # 병원 위치 구하기
      try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        result = cur.fetchall()
        conn.close()
        return result # 검색된 것을 리턴

      except pg.OperationalError as e:
        print(e)
        return 0



def update(table_name, local, domain, passwd, usertype):
    # 수정함수
    sql = f"""UPDATE {table_name} 
              SET usertype = ('{usertype}') 
              WHERE local = ('{local}') AND domain = ('{domain}') AND passwd = ('{passwd}');
           """
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def update_prescription_pharm(name, pharm_name, make_day, comment, prescribe_check):
    # 수정함수
    sql = f"""UPDATE prescription 
              SET pharm_name = ('{pharm_name}'), make_day = ('{make_day}'), comment = ('{comment}'), prescribe_check = ('{prescribe_check}')
              WHERE patient_name = ('{name}')
           """
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def update_prescription_check(name, prescribe_check):
    # 수정함수
    sql = f"""UPDATE prescription 
              SET prescribe_check = ('{prescribe_check}')
              WHERE name = ('{name}');
           """
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def insert_favor_hosp(table_name, name, phone, usertype, hname):
    sql = f"""UPDATE {table_name} 
              SET hname = ('{hname}') 
              WHERE name = ('{name}') AND phone = ('{phone}') AND usertype = ('{usertype}');
           """
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def change_recently(table_name, name, phone, usertype, hname):
    # 수정함수
    sql = f"""UPDATE {table_name} 
              SET recently_hosp = ('{hname}') 
              WHERE name = ('{name}') AND phone = ('{phone}') AND usertype = ('{usertype}');
           """
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)
        return -1

def hosp_list(lat, lng):    
    url = "http://apis.data.go.kr/B551182/hospInfoService/getHospBasisList"
    default_key = "YeQCsOtEPlFjcI9bUk0Cia/As3SzcqtzpSqHFu+41ngyu4Qs4VWW8/aQ3aQueQsin3NUtNzRUnJG59p7kQN/4g=="
    params = {
      'pageNo': 1,
      'numOfRows': 5,
      'ServiceKey': default_key,
      'yPos': lat,
      'xPos': lng,
      'radius': 5000,      
      '_type': 'json'
    }
    r = requests.get(url, params=params)    
    return r.json()

def init_hosp_table():
    table = hosp_list(37.5585146, 127.0331892) # 초기 DB는 한양대 주변 5KM
    info = table['response']['body']['items']['item']
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      for data in info:
            hosp_name = data['yadmNm']
            doctor = data['sdrCnt']
            medical_subject = "종합진료"
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-18시'
            weekend_time = '10시-16시'
            sql = f'''INSERT INTO hosp_table(hosp_name, doctor, medical_subject, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{hosp_name}\', \'{doctor}\', \'{medical_subject}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\', \'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def update_hosp_table(lat, lng):
    table = hosp_list(lat, lng) # 초기 DB는 한양대 주변 5KM
    info = table['response']['body']['items']['item']
    d_sql = f'''TRUNCATE TABLE hosp_table;
             '''
    # 기존 테이블에 있던 내용들 지우기
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      cur.execute(d_sql)
      for data in info:
            hosp_name = data['yadmNm']
            doctor = data['sdrCnt']
            medical_subject = "종합진료(성형외과없음)"
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-18시'
            weekend_time = '10시-16시'
            sql = f'''INSERT INTO hosp_table(hosp_name, doctor, medical_subject, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{hosp_name}\', \'{doctor}\', \'{medical_subject}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\', \'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def update_pharm_table(lat, lng):
    table = pharm_list(lat, lng) # 초기 DB는 한양대 주변 5KM
    info = table['response']['body']['items']['item']
    d_sql = f'''TRUNCATE TABLE pharm_table;
             '''
    # 기존 테이블에 있던 내용들 지우기
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      cur.execute(d_sql)
      for data in info:
            pharm_name = data['yadmNm']
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-21시'
            weekend_time = '10시-18시'
            sql = f'''INSERT INTO pharm_table(pharm_name, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{pharm_name}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\', \'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0


def pharm_list(lat, lng):    
    url = "http://apis.data.go.kr/B551182/pharmacyInfoService/getParmacyBasisList"
    default_key = "YeQCsOtEPlFjcI9bUk0Cia/As3SzcqtzpSqHFu+41ngyu4Qs4VWW8/aQ3aQueQsin3NUtNzRUnJG59p7kQN/4g=="
    params = {
      'pageNo': 1,
      'numOfRows': 5,
      'ServiceKey': default_key,      
      'zipCd': 2010,
      'yPos': lat,
      'xPos': lng,
      'radius': 5000,
      '_type': 'json'
    }
    r = requests.get(url, params=params)
    return r.json()

def init_pharm_table():
    table = pharm_list(37.5585146, 127.0331892) # 초기 DB는 한양대 주변 5KM
    info = table['response']['body']['items']['item']
    try:
      conn = pg.connect(connect_string)
      cur = conn.cursor()
      for data in info:
            pharm_name = data['yadmNm']
            addr = data['addr']
            lng = data['XPos']
            lat = data['YPos']
            distance = data['distance']
            week_time = '09시-21시'
            weekend_time = '10시-18시'
            sql = f'''INSERT INTO pharm_table(pharm_name, addr, lng, lat,
                                              distance, week_time, weekend_time)
                      VALUES (\'{pharm_name}\', \'{addr}\', \'{lng}\',
                              \'{lat}\', \'{distance}\', \'{week_time}\', 
                              \'{weekend_time}\');
                   '''
            print(sql)
            cur.execute(sql)
      conn.commit()
      conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def insert_glasses():
    # 연락처 삽입을 위한 함수
    sql = f'''INSERT INTO glasses
              VALUES ('{"아이온안경원"}', '{"서울특별시 성동구 행당동 12-5 101호"}', '{"02-2299-5848"}', '{"10시-22시"}'), 
                      ('{"룩옵티컬 한대점"}', '{"서울특별시 성동구 행당동 19-54"}', '{"02-2281-6070"}', '{"11시-22시"}'), 
                      ('{"폴라리스 안경원"}', '{"서울특별시 성북구 고려대로24길 15 정암빌딩"}', '{"02-927-9400"}', '{"10시-21시"}'),
                      ('{"탁글라스안경원"}', '{"서울특별시 성동구 왕십리로 410 센트라스 J동 상가 115호"}', '{"02-2281-7378"}', '{"10시-22시"}'), 
                      ('{"룩앤룩안경원"}', '{"서울특별시 성동구 왕십리광장로 17 A01,A02,A03호"}', '{"02-2200-1401"}', '{"10시-21시30분"}'), 
                      ('{"글라스파파안경원"}', '{"서울특별시 성동구 상원길 39 중앙하이츠빌상가 102호"}', '{"02-468-1002"}', '{"10시-21시"}');
           '''
    # 테이블에 이름과 번호를 한 행으로 추가 
    try:
        conn = pg.connect(connect_string) # DB연결(로그인)
        cur = conn.cursor() # DB 작업할 지시자 정하기
        cur.execute(sql) # sql 문을 실행
        # DB에 저장하고 마무리
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)
        return -1
    return 0

def search_glasses_info():
    sql = f'''SELECT name, addr, phone, open_time
              FROM glasses
           '''
    # 병원 위치 구하기
    try:
      conn = pg.connect(connect_string) # DB연결(로그인)
      cur = conn.cursor() # DB 작업할 지시자 정하기
      cur.execute(sql) # sql 문을 실행
      result = cur.fetchall()
      conn.close()
      return result # 검색된 것을 리턴

    except pg.OperationalError as e:
      print(e)
      return 0   
