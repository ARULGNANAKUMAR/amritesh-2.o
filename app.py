from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime, date

app = Flask(__name__)

# Database initialization for Render
def init_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    contact TEXT,
                    address TEXT,
                    blood_group TEXT,
                    emergency_contact TEXT,
                    registered_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialization TEXT,
                    contact TEXT,
                    email TEXT,
                    consultation_fee DECIMAL(10,2),
                    available_days TEXT,
                    available_time TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    doctor_id INTEGER,
                    appointment_date DATE,
                    appointment_time TIME,
                    status TEXT DEFAULT 'Scheduled',
                    reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    doctor_id INTEGER,
                    diagnosis TEXT,
                    prescription TEXT,
                    treatment TEXT,
                    record_date DATE,
                    next_visit DATE,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS billing (
                    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    appointment_id INTEGER,
                    consultation_fee DECIMAL(10,2),
                    medicine_charges DECIMAL(10,2),
                    other_charges DECIMAL(10,2),
                    total_amount DECIMAL(10,2),
                    payment_status TEXT DEFAULT 'Pending',
                    bill_date DATE,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
                )''')
    
    # Insert sample data if empty
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        sample_patients = [
            ('Ramesh Kumar', 45, 'Male', '9876543210', 'Chennai', 'O+', '9876543211'),
            ('Priya Sharma', 32, 'Female', '8765432109', 'Bangalore', 'A+', '8765432110'),
            ('Arun Patel', 28, 'Male', '7654321098', 'Mumbai', 'B+', '7654321099')
        ]
        c.executemany('INSERT INTO patients (name, age, gender, contact, address, blood_group, emergency_contact) VALUES (?,?,?,?,?,?,?)', sample_patients)
        
        sample_doctors = [
            ('Dr. Rajesh Khanna', 'Cardiology', '9123456780', 'dr.rajesh@hospital.com', 800.00, 'Mon,Wed,Fri', '09:00-13:00'),
            ('Dr. Anjali Mehta', 'Pediatrics', '9234567891', 'dr.anjali@hospital.com', 600.00, 'Tue,Thu,Sat', '10:00-14:00'),
            ('Dr. Sanjay Verma', 'Orthopedics', '9345678902', 'dr.sanjay@hospital.com', 700.00, 'Mon-Fri', '14:00-18:00')
        ]
        c.executemany('INSERT INTO doctors (name, specialization, contact, email, consultation_fee, available_days, available_time) VALUES (?,?,?,?,?,?,?)', sample_doctors)
        
        # Sample appointments
        c.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason) VALUES (1, 1, '2024-01-20', '10:00', 'Heart checkup')")
        c.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason) VALUES (2, 2, '2024-01-21', '11:00', 'Child vaccination')")
    
    conn.commit()
    conn.close()

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# ==================== PATIENT APIs ====================
@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO patients (name, age, gender, contact, address, blood_group, emergency_contact) VALUES (?,?,?,?,?,?,?)',
              (data['name'], data['age'], data['gender'], data['contact'], data['address'], data['blood_group'], data['emergency_contact']))
    conn.commit()
    patient_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Patient added successfully!', 'patient_id': patient_id})

@app.route('/get_patients')
def get_patients():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients ORDER BY patient_id DESC').fetchall()
    conn.close()
    return jsonify([dict(patient) for patient in patients])

@app.route('/delete_patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Patient deleted successfully!'})

# ==================== DOCTOR APIs ====================
@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO doctors (name, specialization, contact, email, consultation_fee, available_days, available_time) VALUES (?,?,?,?,?,?,?)',
              (data['name'], data['specialization'], data['contact'], data['email'], data['consultation_fee'], data['available_days'], data['available_time']))
    conn.commit()
    doctor_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Doctor added successfully!', 'doctor_id': doctor_id})

@app.route('/get_doctors')
def get_doctors():
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors ORDER BY doctor_id DESC').fetchall()
    conn.close()
    return jsonify([dict(doctor) for doctor in doctors])

@app.route('/delete_doctor/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM doctors WHERE doctor_id = ?', (doctor_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Doctor deleted successfully!'})

# ==================== APPOINTMENT APIs ====================
@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason) VALUES (?,?,?,?,?)',
              (data['patient_id'], data['doctor_id'], data['appointment_date'], data['appointment_time'], data['reason']))
    conn.commit()
    appointment_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Appointment scheduled successfully!', 'appointment_id': appointment_id})

@app.route('/get_appointments')
def get_appointments():
    conn = get_db_connection()
    appointments = conn.execute('''
        SELECT a.*, p.name as patient_name, d.name as doctor_name, d.specialization 
        FROM appointments a 
        JOIN patients p ON a.patient_id = p.patient_id 
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(appt) for appt in appointments])

@app.route('/update_appointment_status/<int:appointment_id>', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE appointments SET status = ? WHERE appointment_id = ?', 
                 (data['status'], appointment_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Appointment status updated successfully!'})

@app.route('/delete_appointment/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE appointment_id = ?', (appointment_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Appointment deleted successfully!'})

# ==================== MEDICAL RECORDS APIs ====================
@app.route('/add_medical_record', methods=['POST'])
def add_medical_record():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO medical_records (patient_id, doctor_id, diagnosis, prescription, treatment, record_date, next_visit) VALUES (?,?,?,?,?,?,?)',
              (data['patient_id'], data['doctor_id'], data['diagnosis'], data['prescription'], data['treatment'], data['record_date'], data['next_visit']))
    conn.commit()
    record_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Medical record added successfully!', 'record_id': record_id})

@app.route('/get_medical_records')
def get_medical_records():
    conn = get_db_connection()
    records = conn.execute('''
        SELECT mr.*, p.name as patient_name, d.name as doctor_name 
        FROM medical_records mr 
        JOIN patients p ON mr.patient_id = p.patient_id 
        JOIN doctors d ON mr.doctor_id = d.doctor_id
        ORDER BY mr.record_id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(record) for record in records])

@app.route('/get_patient_medical_records/<int:patient_id>')
def get_patient_medical_records(patient_id):
    conn = get_db_connection()
    records = conn.execute('''
        SELECT mr.*, d.name as doctor_name 
        FROM medical_records mr 
        JOIN doctors d ON mr.doctor_id = d.doctor_id 
        WHERE mr.patient_id = ?
        ORDER BY mr.record_date DESC
    ''', (patient_id,)).fetchall()
    conn.close()
    return jsonify([dict(record) for record in records])

# ==================== BILLING APIs ====================
@app.route('/add_bill', methods=['POST'])
def add_bill():
    data = request.json
    total = float(data['consultation_fee']) + float(data['medicine_charges']) + float(data['other_charges'])
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO billing (patient_id, appointment_id, consultation_fee, medicine_charges, other_charges, total_amount, payment_status, bill_date) VALUES (?,?,?,?,?,?,?,?)',
              (data['patient_id'], data['appointment_id'], data['consultation_fee'], data['medicine_charges'], data['other_charges'], total, data['payment_status'], data['bill_date']))
    conn.commit()
    bill_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Bill added successfully!', 'bill_id': bill_id, 'total_amount': total})

@app.route('/get_bills')
def get_bills():
    conn = get_db_connection()
    bills = conn.execute('''
        SELECT b.*, p.name as patient_name 
        FROM billing b 
        JOIN patients p ON b.patient_id = p.patient_id
        ORDER BY b.bill_id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(bill) for bill in bills])

@app.route('/update_bill_status/<int:bill_id>', methods=['PUT'])
def update_bill_status(bill_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE billing SET payment_status = ? WHERE bill_id = ?', 
                 (data['payment_status'], bill_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bill status updated successfully!'})

# ==================== DASHBOARD API ====================
@app.route('/get_dashboard_stats')
def get_dashboard_stats():
    conn = get_db_connection()
    
    total_patients = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    total_doctors = conn.execute('SELECT COUNT(*) FROM doctors').fetchone()[0]
    total_appointments = conn.execute('SELECT COUNT(*) FROM appointments').fetchone()[0]
    today_appointments = conn.execute('SELECT COUNT(*) FROM appointments WHERE appointment_date = ?', 
                                     (date.today().isoformat(),)).fetchone()[0]
    pending_bills = conn.execute('SELECT COUNT(*) FROM billing WHERE payment_status = "Pending"').fetchone()[0]
    total_revenue = conn.execute('SELECT SUM(total_amount) FROM billing WHERE payment_status = "Paid"').fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_bills': pending_bills,
        'total_revenue': float(total_revenue)
    })

# ==================== SEARCH APIs ====================
@app.route('/search_patients/<string:query>')
def search_patients(query):
    conn = get_db_connection()
    patients = conn.execute('''
        SELECT * FROM patients 
        WHERE name LIKE ? OR contact LIKE ? OR blood_group LIKE ?
        ORDER BY patient_id DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return jsonify([dict(patient) for patient in patients])

@app.route('/search_doctors/<string:query>')
def search_doctors(query):
    conn = get_db_connection()
    doctors = conn.execute('''
        SELECT * FROM doctors 
        WHERE name LIKE ? OR specialization LIKE ? OR contact LIKE ?
        ORDER BY doctor_id DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return jsonify([dict(doctor) for doctor in doctors])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
