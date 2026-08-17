import sqlite3
import hashlib
import os
from pathlib import Path
from enum import Enum


class LogType(Enum):
    """로그 타입 정의"""
    LOGIN = "login"                     # 로그인
    LOGOUT = "logout"                   # 로그아웃
    FACE_AUTH = "face_auth"             # 얼굴 인증


class DatabaseManager:
    def __init__(self, db_path="data/database.db"):
        """데이터베이스 초기화"""
        self.db_path = db_path
        
        # data 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.create_tables()

    def get_connection(self):
        """데이터베이스 연결"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False,
        )
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def create_tables(self):
        """회원 테이블 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 유저 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT (datetime('now','localtime'))
            )
        ''')

        # 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                log_type TEXT NOT NULL,
                datetime DATETIME DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """비밀번호 해싱 (SHA-256)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, password_confirm):
        """회원 등록"""
        conn = None
        try:
            # 비밀번호 일치 여부 확인
            if password != password_confirm:
                return False, "비밀번호가 일치하지 않습니다."

            # 비밀번호 길이 확인
            if len(password) < 4:
                return False, "비밀번호는 4자 이상이어야 합니다."

            # 아이디 길이 확인
            if len(username) < 3:
                return False, "아이디는 3자 이상이어야 합니다."

            conn = self.get_connection()
            cursor = conn.cursor()

            # 비밀번호 해싱
            hashed_password = self.hash_password(password)

            # 사용자 추가
            cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, hashed_password))

            conn.commit()
            return True, "회원 등록 성공!"

        except sqlite3.IntegrityError:
            return False, "이미 존재하는 아이디입니다."
        except Exception as e:
            return False, f"오류 발생: {str(e)}"
        finally:
            if conn is not None:
                conn.close()

    def check_user(self, username, password):
        """로그인 확인"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)

            cursor.execute('''
                SELECT id FROM users 
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))

            user = cursor.fetchone()

            if user:
                # 로그인 로그 기록
                self.log_event(username, LogType.LOGIN)
                return True, "로그인 성공!"
            else:
                return False, "아이디 또는 비밀번호가 잘못되었습니다."

        except Exception as e:
            return False, f"오류 발생: {str(e)}"
        finally:
            if conn is not None:
                conn.close()

    def user_exists(self, username):
        """아이디 중복 확인"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            return user is not None

        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return False
        finally:
            if conn is not None:
                conn.close()

    def log_event(self, username, log_type):
        """로그 기록"""
        conn = None
        try:
            if not isinstance(log_type, LogType):
                return False, "유효하지 않은 로그 타입입니다."

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO logs (username, log_type)
                VALUES (?, ?)
            ''', (username, log_type.value))

            conn.commit()
            return True, "로그 기록 성공"

        except Exception as e:
            return False, f"로그 기록 오류: {str(e)}"
        finally:
            if conn is not None:
                conn.close()

    def get_logs(self, username=None, limit=10):
        """로그 조회"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if username:
                cursor.execute('''
                    SELECT id, username, log_type, datetime 
                    FROM logs 
                    WHERE username = ?
                    ORDER BY datetime DESC
                    LIMIT ?
                ''', (username, limit))
            else:
                cursor.execute('''
                    SELECT id, username, log_type, datetime 
                    FROM logs 
                    ORDER BY datetime DESC
                    LIMIT ?
                ''', (limit,))

            logs = cursor.fetchall()
            return logs

        except Exception as e:
            print(f"로그 조회 오류: {str(e)}")
            return []
        finally:
            if conn is not None:
                conn.close()