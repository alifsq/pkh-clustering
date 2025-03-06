from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inisialisasi SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

def configure_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/pkhclusteringdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'admin13579'
    db.init_app(app)

    # Membuat tabel jika belum ada
    with app.app_context():
        db.create_all()



# Contoh model
class DataPenerima(db.Model):
    __tablename__ = 'datapenerima'
    id_penerima = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.DateTime, default=db.func.current_timestamp())
    nik = db.Column(db.String(17), unique=True, nullable=False)  # Disesuaikan dengan panjang NIK sebenarnya
    nama = db.Column(db.String(100), nullable=False)  # Memberi ruang lebih untuk nama
    k_rumah = db.Column(db.String(20), nullable=False)  # Nama kolom lebih deskriptif
    pekerjaan = db.Column(db.String(50), nullable=False)  # Memberi ruang lebih untuk nama pekerjaan
    gaji = db.Column(db.BigInteger, nullable=False)  # Mendukung gaji dalam nilai besar
    
    def __repr__(self):
        return f"<DataPenerima {self.nama}>"
    # Hubungan dengan transformeddata
    transformed_data = db.relationship('TransformedData', backref='datapenerima', cascade="all, delete-orphan")

class TransformedData(db.Model):
    __tablename__ = 'transformeddata'
    id_transform = db.Column(db.Integer, primary_key=True)
    id_penerima = db.Column(db.Integer, db.ForeignKey('datapenerima.id_penerima'), nullable=False)
    transformed_k_rumah = db.Column(db.Integer, nullable=False)
    transformed_gaji = db.Column(db.Integer, nullable=False)
    transformed_pekerjaan = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f"<TransformedData {self.id_transform}>"
  
class Hasilduacluster(db.Model):
    __tablename__ = 'hasilduacluster'
    id = db.Column(db.Integer, primary_key=True)
    id_penerima = db.Column(db.Integer, db.ForeignKey('datapenerima.id_penerima'), nullable=False)
    cluster = db.Column(db.Integer, nullable=False)
    data_penerima = db.relationship('DataPenerima', backref='hasilduacluster')

class Hasiltigacluster(db.Model):
    __tablename__ = 'hasiltigacluster'
    id = db.Column(db.Integer, primary_key=True)
    id_penerima = db.Column(db.Integer, db.ForeignKey('datapenerima.id_penerima'), nullable=False)
    cluster = db.Column(db.Integer, nullable=False)
    data_penerima = db.relationship('DataPenerima', backref='hasiltigacluster')
    
class HasilClustering(db.Model):
    __tablename__ = 'hasil_clustering'
    id = db.Column(db.Integer, primary_key=True)
    id_penerima = db.Column(db.Integer, db.ForeignKey('datapenerima.id_penerima'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)  # Hasil clustering
    
    # Relasi ke DataPenerima
    data_penerima = db.relationship('DataPenerima', backref='hasil_clustering')

    def __repr__(self):
        return f"<HasilClustering {self.id_penerima} - Cluster {self.cluster_id}>"
