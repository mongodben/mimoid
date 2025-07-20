"""Database seeder for Cogna Educação Brazilian EdTech Platform

Creates realistic sample data for educational technology platform serving 2.4 million Brazilian students
with government funding programs (FIES/Prouni), multi-institutional operations, and comprehensive
document management workflows.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
from faker import Faker
from faker.providers import BaseProvider
from decimal import Decimal

from mimiod import DatabaseSeeder
from db_schema import (
    Institution, Student, Application, Document, Staff, Course, Program, Enrollment, 
    Assessment, Content, FinancialAid, ApplicationStatus, 
    FundingProgram, DocumentType, DocumentStatus, StudentStatus, 
    StaffRole, CourseStatus, EnrollmentStatus, AssessmentType, GradeStatus,
    database_schema
)


class BrazilianEducationProvider(BaseProvider):
    """Custom Faker provider for Brazilian education sector data with diverse naming patterns"""
    
    # Diverse Brazilian surnames reflecting different ethnic backgrounds
    brazilian_surnames = [
        # Portuguese origin (most common)
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
        "Lima", "Gomes", "Ribeiro", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes",
        "Vieira", "Barbosa", "Rocha", "Dias", "Monteiro", "Mendes", "Cardoso", "Reis",
        
        # Italian influence 
        "Rossi", "Ferrari", "Bianchi", "Romano", "Ricci", "Marino", "Greco", "Bruno",
        "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo",
        
        # German influence (Southern Brazil)
        "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
        "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein",
        
        # Japanese influence (largest Japanese community outside Japan)
        "Yamamoto", "Tanaka", "Watanabe", "Ito", "Sato", "Suzuki", "Takahashi", "Nakamura",
        "Hayashi", "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki", "Yamaguchi",
        
        # African influence
        "Conceição", "Nascimento", "Sacramento", "Esperança", "Liberdade", "Vitória",
        "Paz", "Fé", "Carmo", "Graça", "Luz", "Bonfim", "Santana", "Cruz",
        
        # Indigenous influence
        "Tupinambá", "Guarani", "Araújo", "Iracema", "Ubirajara", "Jaci", "Aracy",
        "Cauã", "Iara", "Raoni", "Jurema", "Potira", "Moema", "Rudá",
        
        # Lebanese/Arabic influence (significant community)
        "Mansur", "Salim", "Nader", "Farah", "Haddad", "Maluf", "Rahall", "Sabbag",
        "Tahan", "Zogbi", "Kalil", "Batista", "Nasser", "Chalub", "Daud"
    ]
    
    # Diverse Brazilian first names reflecting multicultural heritage
    brazilian_male_names = [
        # Traditional Portuguese names
        "João", "José", "Antônio", "Francisco", "Carlos", "Paulo", "Pedro", "Lucas", "Mateus",
        "Luiz", "Marcos", "Bruno", "Rafael", "Daniel", "Fábio", "Rodrigo", "Fernando", "Gustavo",
        
        # Modern Brazilian names
        "Gabriel", "Matheus", "Arthur", "Enzo", "Nicolas", "Lorenzo", "Miguel", "Davi", "Bernardo",
        "Samuel", "Ryan", "Cauã", "Anthony", "Ian", "Levi", "Noah", "Theo", "Benjamin",
        
        # Indigenous names
        "Cauã", "Ubiratan", "Raoni", "Iuri", "Kaique", "Kauê", "Rudá", "Iracema", "Tupã",
        "Guaraci", "Jaci", "Potira", "Moema", "Moacir", "Yuri", "Kléber", "Caio",
        
        # Italian influence
        "Marco", "Alessandro", "Giuliano", "Adriano", "Fabrizio", "Márcio", "Sérgio", "Cláudio",
        "Roberto", "Flávio", "Vítor", "Diego", "Édson", "Ronaldo", "Ricardo", "Anderson",
        
        # African influence 
        "Luanda", "Angola", "Benedito", "Severino", "Joaquim", "Sebastião", "Gilberto", "Washington",
        "Jefferson", "Edson", "Robson", "Jackson", "Wellington", "Emerson", "Everton", "Cleiton"
    ]
    
    brazilian_female_names = [
        # Traditional Portuguese names
        "Maria", "Ana", "Francisca", "Antônia", "Adriana", "Juliana", "Márcia", "Fernanda",
        "Patricia", "Aline", "Sandra", "Cristiane", "Kelly", "Vanessa", "Simone", "Daniela",
        
        # Modern Brazilian names  
        "Sophia", "Alice", "Julia", "Isabella", "Manuela", "Laura", "Luiza", "Valentina",
        "Giovanna", "Helena", "Beatriz", "Mariana", "Emanuelly", "Yasmin", "Lara", "Lívia",
        
        # Indigenous names
        "Iara", "Jaci", "Potira", "Moema", "Jurema", "Aracy", "Iracema", "Raissa", "Tainá",
        "Kauane", "Mayara", "Luana", "Bianca", "Vitória", "Gabriela", "Camila", "Letícia",
        
        # Italian influence
        "Giulia", "Chiara", "Francesca", "Valentina", "Giorgia", "Martina", "Sara", "Elisa",
        "Federica", "Silvia", "Paola", "Roberta", "Monica", "Cristina", "Claudia", "Angela",
        
        # African influence
        "Conceição", "Aparecida", "Benedita", "Sebastiana", "Josefina", "Terezinha", "Luzia",
        "Esperança", "Vitória", "Graça", "Fátima", "Socorro", "Rosário", "Salete", "Nair"
    ]
    
    # Brazilian cities with their corresponding states (realistic combinations)
    brazilian_cities_states = {
        # São Paulo (most populous state)
        "São Paulo": "São Paulo",
        "Guarulhos": "São Paulo", 
        "Campinas": "São Paulo",
        "São Bernardo do Campo": "São Paulo",
        "Santo André": "São Paulo",
        "São José dos Campos": "São Paulo",
        "Ribeirão Preto": "São Paulo",
        "Sorocaba": "São Paulo",
        
        # Rio de Janeiro
        "Rio de Janeiro": "Rio de Janeiro",
        "São Gonçalo": "Rio de Janeiro",
        "Duque de Caxias": "Rio de Janeiro",
        "Nova Iguaçu": "Rio de Janeiro",
        "Niterói": "Rio de Janeiro",
        "Campos dos Goytacazes": "Rio de Janeiro",
        
        # Minas Gerais  
        "Belo Horizonte": "Minas Gerais",
        "Uberlândia": "Minas Gerais",
        "Contagem": "Minas Gerais",
        "Juiz de Fora": "Minas Gerais",
        
        # Bahia
        "Salvador": "Bahia",
        "Feira de Santana": "Bahia",
        "Vitória da Conquista": "Bahia",
        "Camaçari": "Bahia",
        
        # Paraná
        "Curitiba": "Paraná",
        "Londrina": "Paraná",
        "Maringá": "Paraná",
        "Ponta Grossa": "Paraná",
        
        # Rio Grande do Sul
        "Porto Alegre": "Rio Grande do Sul",
        "Caxias do Sul": "Rio Grande do Sul",
        "Pelotas": "Rio Grande do Sul",
        "Canoas": "Rio Grande do Sul",
        
        # Pernambuco
        "Recife": "Pernambuco",
        "Jaboatão dos Guararapes": "Pernambuco",
        "Olinda": "Pernambuco",
        "Caruaru": "Pernambuco",
        
        # Ceará
        "Fortaleza": "Ceará",
        "Caucaia": "Ceará",
        "Juazeiro do Norte": "Ceará",
        "Maracanaú": "Ceará",
        
        # Pará
        "Belém": "Pará",
        "Ananindeua": "Pará",
        "Santarém": "Pará",
        "Marabá": "Pará",
        
        # Santa Catarina
        "Florianópolis": "Santa Catarina",
        "Joinville": "Santa Catarina",
        "Blumenau": "Santa Catarina",
        "São José": "Santa Catarina",
        
        # Goiás
        "Goiânia": "Goiás",
        "Aparecida de Goiânia": "Goiás",
        "Anápolis": "Goiás",
        "Rio Verde": "Goiás",
        
        # Maranhão
        "São Luís": "Maranhão",
        "Imperatriz": "Maranhão",
        "São José de Ribamar": "Maranhão",
        "Timon": "Maranhão",
        
        # Paraíba
        "João Pessoa": "Paraíba",
        "Campina Grande": "Paraíba",
        "Santa Rita": "Paraíba",
        "Patos": "Paraíba",
        
        # Mato Grosso
        "Cuiabá": "Mato Grosso",
        "Várzea Grande": "Mato Grosso",
        "Rondonópolis": "Mato Grosso",
        "Sinop": "Mato Grosso",
        
        # Amazonas
        "Manaus": "Amazonas",
        "Parintins": "Amazonas",
        "Itacoatiara": "Amazonas",
        "Manacapuru": "Amazonas",
        
        # Distrito Federal
        "Brasília": "Distrito Federal",
        
        # Mato Grosso do Sul
        "Campo Grande": "Mato Grosso do Sul",
        "Dourados": "Mato Grosso do Sul",
        "Três Lagoas": "Mato Grosso do Sul",
        "Corumbá": "Mato Grosso do Sul",
        
        # Piauí
        "Teresina": "Piauí",
        "Parnaíba": "Piauí",
        "Picos": "Piauí",
        "Piripiri": "Piauí",
        
        # Alagoas
        "Maceió": "Alagoas",
        "Arapiraca": "Alagoas",
        "Palmeira dos Índios": "Alagoas",
        "Rio Largo": "Alagoas",
        
        # Rio Grande do Norte
        "Natal": "Rio Grande do Norte",
        "Mossoró": "Rio Grande do Norte",
        "Parnamirim": "Rio Grande do Norte",
        "São Gonçalo do Amarante": "Rio Grande do Norte",
        
        # Espírito Santo
        "Vitória": "Espírito Santo",
        "Vila Velha": "Espírito Santo",
        "Cariacica": "Espírito Santo",
        "Serra": "Espírito Santo",
        
        # Sergipe
        "Aracaju": "Sergipe",
        "Nossa Senhora do Socorro": "Sergipe",
        "Lagarto": "Sergipe",
        "Itabaiana": "Sergipe",
        
        # Rondônia
        "Porto Velho": "Rondônia",
        "Ji-Paraná": "Rondônia",
        "Ariquemes": "Rondônia",
        "Vilhena": "Rondônia",
        
        # Acre
        "Rio Branco": "Acre",
        "Cruzeiro do Sul": "Acre",
        "Sena Madureira": "Acre",
        "Tarauacá": "Acre",
        
        # Amapá
        "Macapá": "Amapá",
        "Santana": "Amapá",
        "Laranjal do Jari": "Amapá",
        "Oiapoque": "Amapá",
        
        # Roraima
        "Boa Vista": "Roraima",
        "Rorainópolis": "Roraima",
        "Caracaraí": "Roraima",
        "Alto Alegre": "Roraima",
        
        # Tocantins
        "Palmas": "Tocantins",
        "Araguaína": "Tocantins",
        "Gurupi": "Tocantins",
        "Porto Nacional": "Tocantins"
    }
    
    # Academic programs popular in Brazil
    academic_programs = [
        "Administração", "Direito", "Engenharia Civil", "Medicina", "Enfermagem", "Pedagogia",
        "Psicologia", "Ciências Contábeis", "Engenharia de Produção", "Sistemas de Informação",
        "Educação Física", "Fisioterapia", "Arquitetura e Urbanismo", "Engenharia Mecânica",
        "Farmácia", "Nutrição", "Odontologia", "Engenharia Elétrica", "Matemática", "História",
        "Geografia", "Letras", "Biologia", "Química", "Física", "Sociologia", "Filosofia",
        "Comunicação Social", "Design Gráfico", "Turismo", "Gastronomia", "Marketing"
    ]
    
    # Brazilian CPF generation (simplified for demo)
    def brazilian_cpf(self) -> str:
        """Generate a realistic Brazilian CPF format (simplified for demo purposes)"""
        # Generate 9 random digits
        digits = [random.randint(0, 9) for _ in range(9)]
        
        # Calculate first check digit
        sum1 = sum(digits[i] * (10 - i) for i in range(9))
        check1 = 11 - (sum1 % 11)
        if check1 >= 10:
            check1 = 0
        
        # Calculate second check digit
        digits_with_check1 = digits + [check1]
        sum2 = sum(digits_with_check1[i] * (11 - i) for i in range(10))
        check2 = 11 - (sum2 % 11)
        if check2 >= 10:
            check2 = 0
        
        # Format as string (exactly 14 characters: ###.###.###-##)
        return f"{digits[0]}{digits[1]}{digits[2]}.{digits[3]}{digits[4]}{digits[5]}.{digits[6]}{digits[7]}{digits[8]}-{check1}{check2}"
    
    def brazilian_rg(self) -> str:
        """Generate Brazilian RG format"""
        digits = [random.randint(0, 9) for _ in range(8)]
        state_codes = ["SP", "RJ", "MG", "BA", "PR", "RS", "PE", "CE", "PA", "SC", "GO", "MA"]
        state = random.choice(state_codes)
        return f"{digits[0]}{digits[1]}.{digits[2]}{digits[3]}{digits[4]}.{digits[5]}{digits[6]}{digits[7]}-{state}"
    
    def brazilian_phone(self) -> str:
        """Generate Brazilian phone number"""
        area_codes = ["11", "21", "31", "41", "51", "61", "71", "81", "85", "62", "91", "47"]
        area = random.choice(area_codes)
        mobile_prefix = random.choice(["9", "8", "7"])
        number = "".join([str(random.randint(0, 9)) for _ in range(8)])
        return f"({area}) {mobile_prefix}{number[:4]}-{number[4:]}"
    
    def brazilian_postal_code(self) -> str:
        """Generate Brazilian postal code (CEP)"""
        return f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    def brazilian_full_name(self) -> tuple:
        """Generate diverse Brazilian full name (first_name, last_name)"""
        gender = random.choice(["male", "female"])
        if gender == "male":
            first_name = random.choice(self.brazilian_male_names)
        else:
            first_name = random.choice(self.brazilian_female_names)
        
        # Sometimes use compound names (common in Brazil)
        if random.random() < 0.3:  # 30% chance of compound name
            if gender == "male":
                second_name = random.choice(self.brazilian_male_names)
            else:
                second_name = random.choice(self.brazilian_female_names)
            first_name = f"{first_name} {second_name}"
        
        # Generate surname (sometimes compound)
        surname = random.choice(self.brazilian_surnames)
        if random.random() < 0.4:  # 40% chance of compound surname
            second_surname = random.choice(self.brazilian_surnames)
            surname = f"{surname} {second_surname}"
            
        return first_name, surname

    def brazilian_university_name(self) -> str:
        """Generate Brazilian university name"""
        types = ["Universidade", "Centro Universitário", "Faculdade", "Instituto"]
        qualifiers = ["Federal", "Estadual", "Católica", "Metodista", "Presbiteriana", "Adventista"]
        location = random.choice(list(self.brazilian_cities_states.keys()))
        
        if random.random() < 0.3:  # Federal/State institutions
            qualifier = random.choice(["Federal", "Estadual"])
            return f"{random.choice(types)} {qualifier} de {location}"
        else:  # Private institutions
            qualifier = random.choice(qualifiers[2:])  # Religious or other private
            return f"{random.choice(types)} {qualifier} de {location}"
    
    def academic_program(self) -> str:
        """Get random academic program popular in Brazil"""
        return random.choice(self.academic_programs)
    
    def brazilian_city_state(self) -> tuple:
        """Get random Brazilian city with its corresponding state (realistic combination)"""
        city = random.choice(list(self.brazilian_cities_states.keys()))
        state = self.brazilian_cities_states[city]
        return city, state
    
    def brazilian_city(self) -> str:
        """Get random Brazilian city"""
        return random.choice(list(self.brazilian_cities_states.keys()))
    
    def brazilian_state(self) -> str:
        """Get random Brazilian state"""
        return random.choice(list(set(self.brazilian_cities_states.values())))


class BrazilianEdTechSeeder(DatabaseSeeder):
    """Database seeder for Brazilian EdTech platform with diverse naming patterns"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        super().__init__(connection_string, database_schema)
        # Create Brazilian Portuguese locale for Faker
        self.fake = Faker('pt_BR')  # Portuguese (Brazil) 
        self.fake.add_provider(BrazilianEducationProvider)
        
        # Track created references for relationships
        self.institution_ids: List[str] = []
        self.student_ids: List[str] = []
        self.staff_ids: List[str] = []
        self.course_ids: List[str] = []
        self.application_ids: List[str] = []
        
        # Database connection
        from pymongo import MongoClient
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        
        # Brazilian education specific data (only valid FundingProgram enum values)
        self.funding_programs = [
            ("FIES", "Student Financing Fund - Government low-interest loans"),
            ("ProUni", "University for All Program - Scholarships for low-income students"),
            ("institutional_scholarship", "Institutional Scholarship Program"),
            ("merit_scholarship", "Merit-based Scholarship"),
            ("need_based_aid", "Need-based Financial Aid")
        ]
        
        # Document types matching DocumentType enum values
        self.document_types_info = {
            "identity_document": "Brazilian identity document (CPF/RG)",
            "proof_of_income": "Family income declaration for funding eligibility",
            "academic_transcript": "Academic transcript with grades",
            "birth_certificate": "Birth certificate",
            "proof_of_residence": "Proof of residence document",
            "bank_statement": "Bank account statement",
            "tax_declaration": "Income tax declaration",
            "employment_letter": "Employment verification letter",
            "medical_certificate": "Medical certificate",
            "military_certificate": "Military service certificate",
            "voter_registration": "Electoral registration document"
        }
    
    def generate_id(self) -> str:
        """Generate a unique ObjectId string"""
        from bson import ObjectId
        return str(ObjectId())
    
    def bulk_insert(self, collection_name: str, documents: List[Any]):
        """Insert documents into collection in bulk"""
        if documents:
            # Convert Pydantic models to dicts
            dict_documents = []
            for doc in documents:
                if hasattr(doc, 'dict'):
                    dict_documents.append(doc.dict())
                else:
                    dict_documents.append(doc)
            
            self.db[collection_name].insert_many(dict_documents)
    
    def create_database_schema(self):
        """Create database schema with indexes"""
        # Create collections and indexes
        for collection_name, collection_schema in self.database_schema.collections.items():
            collection = self.db[collection_name]
            
            # Create indexes
            for index in collection_schema.indexes:
                try:
                    collection.create_index(
                        list(index.keys.items()),
                        unique=index.unique,
                        sparse=index.sparse,
                        name=index.name
                    )
                except Exception as e:
                    print(f"Warning: Could not create index {index.name}: {e}")
    
    def drop_database(self):
        """Drop the entire database"""
        self.client.drop_database(self.database_schema.database_name)
    
    def test_connection(self):
        """Test database connection"""
        self.client.admin.command('ismaster')
    
    def seed_institutions(self, count: int = 12):
        """Create Brazilian educational institutions across different types"""
        print(f"🏫 Seeding {count} Brazilian educational institutions...")
        
        institutions = []
        for _ in range(count):
            institution_id = self.generate_id()
            
            # Choose institution type with realistic distribution
            institution_types = ["Universidade", "Centro Universitário", "Faculdade", "Instituto Federal"]
            institution_type = random.choices(
                institution_types,
                weights=[25, 35, 30, 10],  # Higher weight for universities and colleges
                k=1
            )[0]
            
            # Generate Brazilian university name
            institution_name = self.fake.brazilian_university_name()
            
            # Create realistic Brazilian addresses
            city, state = self.fake.brazilian_city_state()
            
            institution = Institution(
                _id=institution_id,
                name=institution_name,
                short_name=institution_name.split()[0][:10],  # First word as short name
                institution_code=f"INST{random.randint(1000, 9999)}",
                institution_type=institution_type,
                
                # Address information
                address={
                    "street": self.fake.street_address(),
                    "neighborhood": f"Bairro {self.fake.word().capitalize()}",
                    "country": "Brazil"
                },
                city=city,
                state=state,
                postal_code=self.fake.brazilian_postal_code(),
                
                # Contact information with Brazilian format
                phone=self.fake.brazilian_phone(),
                email=f"contato@{institution_name.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')}.edu.br",
                website=f"www.{institution_name.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')}.edu.br",
                
                # Educational details
                accreditation_level=random.choice(["Credenciada", "Recredenciada", "Em Supervisão"]),
                founded_year=random.randint(1950, 2020),
                
                # Operational information  
                total_students=random.randint(5000, 50000),
                total_faculty=random.randint(200, 2000),
                total_staff=random.randint(100, 1000),
                
                # Compliance and certification
                mec_code=f"MEC{random.randint(100000, 999999)}",  # Ministry of Education code
                quality_rating=random.choice(["3", "4", "5"]),  # MEC quality scale
                
                # Academic offerings
                degree_levels=random.sample(["Graduação", "Pós-graduação", "Mestrado", "Doutorado"], k=random.randint(2, 4)),
                academic_areas=[self.fake.academic_program() for _ in range(random.randint(5, 15))],
                
                # Financial aid participation
                participates_fies=random.choice([True, False]),
                participates_prouni=random.choice([True, False]),
                
                # Status
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            institutions.append(institution)
            self.institution_ids.append(institution_id)
        
        self.bulk_insert("institutions", institutions)
        print(f"  ✅ Created {len(institutions)} institutions with diverse Brazilian names")

    def seed_students(self, count: int = 5000):
        """Create Brazilian students with diverse naming patterns"""
        print(f"👨‍🎓 Seeding {count} Brazilian students with diverse names...")
        
        students = []
        batch_size = 1000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_students = []
            
            for i in range(batch_start, batch_end):
                student_id = self.generate_id()
                
                # Generate diverse Brazilian names
                first_name, last_name = self.fake.brazilian_full_name()
                
                # Create realistic date ranges for Brazilian students
                birth_date = self.fake.date_time_between(start_date='-30y', end_date='-16y')
                enrollment_date = self.fake.date_time_between(start_date='-5y', end_date='now')
                
                # Generate realistic city-state combination
                student_city, student_state = self.fake.brazilian_city_state()
                
                student = Student(
                    _id=student_id,
                    
                    # Diverse Brazilian personal information
                    first_name=first_name,
                    last_name=last_name,
                    full_name=f"{first_name} {last_name}",
                    email=f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}@email.com",
                    
                    # Required student fields
                    student_id=f"STU{i+1:06d}",
                    primary_institution_id=random.choice(self.institution_ids),
                    
                    # Brazilian identification documents
                    cpf=self.fake.brazilian_cpf(),
                    rg=self.fake.brazilian_rg(),
                    
                    # Personal details
                    birth_date=birth_date,
                    birth_place=f"{student_city}, {student_state}",
                    gender=random.choice(["male", "female", "other"]),
                    phone=self.fake.brazilian_phone(),
                    
                    # Brazilian address (realistic city-state combination)
                    address={
                        "street": self.fake.street_address(),
                        "neighborhood": f"Bairro {self.fake.word().capitalize()}",
                        "country": "Brazil"
                    },
                    city=student_city,
                    state=student_state,
                    postal_code=self.fake.brazilian_postal_code(),
                    
                    # Emergency contact (required)
                    emergency_contact={
                        "name": f"{self.fake.brazilian_full_name()[0]} {self.fake.brazilian_full_name()[1]}",
                        "relationship": random.choice(["pai", "mãe", "cônjuge", "irmão", "tia"]),
                        "phone": self.fake.brazilian_phone()
                    },
                    
                    # Status
                    # Most fields simplified to match schema
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                batch_students.append(student)
                self.student_ids.append(student_id)
            
            self.bulk_insert("students", batch_students)
            students.extend(batch_students)
            print(f"  📚 Created batch {batch_start//batch_size + 1}: {len(batch_students)} students")
        
        print(f"  ✅ Created {len(students)} students with diverse Brazilian naming patterns")

    def seed_applications(self, count: int = 15000):
        """Create FIES/ProUni funding applications with Brazilian patterns"""
        print(f"📄 Seeding {count} FIES/ProUni applications...")
        
        applications = []
        batch_size = 1000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_applications = []
            
            for i in range(batch_start, batch_end):
                application_id = self.generate_id()
                
                # Application timing - concentrated in semester periods
                if random.random() < 0.6:  # 60% in main application periods
                    application_date = self.fake.date_time_between(
                        start_date=datetime(2023, 1, 15), 
                        end_date=datetime(2023, 2, 15)  # Main application period
                    )
                else:
                    application_date = self.fake.date_time_between(start_date='-1y', end_date='now')
                
                # Funding program selection
                funding_program, program_description = random.choice(self.funding_programs[:2])  # Focus on FIES/ProUni
                
                program_id = random.choice(self.program_ids) if hasattr(self, 'program_ids') and self.program_ids else self.generate_id()
                deadline = application_date + timedelta(days=30)
                
                application = Application(
                    _id=application_id,
                    
                    # Required identification fields
                    application_number=f"APP{application_date.year}{i+1:08d}",
                    protocol_number=f"PROT{random.randint(1000000, 9999999)}",
                    student_id=random.choice(self.student_ids),
                    institution_id=random.choice(self.institution_ids),
                    program_id=program_id,
                    
                    # Required funding details
                    funding_program=FundingProgram(funding_program.lower()),
                    requested_amount=random.uniform(20000, 150000),
                    funding_percentage=random.uniform(0.5, 1.0),  # 50-100% funding
                    
                    # Required timeline
                    submission_date=application_date,
                    deadline_date=deadline,
                    decision_date=application_date + timedelta(days=random.randint(45, 90)) if random.random() < 0.7 else None,
                    
                    # Required application form as dictionary
                    application_form={
                        "requested_semester": f"{application_date.year}/{1 if application_date.month <= 6 else 2}",
                        "program_name": self.fake.academic_program(),
                        "enem_score": random.randint(300, 990),
                        "high_school_gpa": random.uniform(6.0, 10.0),
                        "high_school_type": random.choice(["public", "private", "mixed"]),
                        "is_cadunico_registered": random.choice([True, False])
                    },
                    
                    # Required financial information
                    family_income_declared=random.uniform(1000, 8000),  # Monthly family income in BRL
                    dependents_count=random.randint(0, 5),
                    employment_status=random.choice(["unemployed", "part_time", "full_time", "student", "self_employed"]),
                    
                    # Required documents list (max 11 available document types)
                    required_documents=random.sample(list(DocumentType), k=random.randint(5, 11)),
                    
                    # Status and processing
                    status=random.choice(list(ApplicationStatus)),
                    current_stage=random.choice(["initial_review", "document_verification", "eligibility_check", "final_review"]),
                    
                    # Government system integration
                    fies_protocol=f"FIES{random.randint(100000, 999999)}" if funding_program.lower() == "fies" else None,
                    prouni_protocol=f"PROUNI{random.randint(100000, 999999)}" if funding_program.lower() == "prouni" else None,
                    government_status=random.choice(["pending", "submitted", "approved", "rejected"]),
                    
                    # Verification statuses
                    data_verification_status=random.choice(["pending", "verified", "requires_review"]),
                    fraud_check_status=random.choice(["pending", "cleared", "flagged"]),
                    compliance_status=random.choice(["pending", "compliant", "non_compliant"]),
                    
                    # Decision information
                    decision=random.choice(["approved", "rejected", "conditional"]) if random.random() < 0.7 else None,
                    approved_amount=random.uniform(15000, 120000) if random.random() < 0.6 else None,
                    
                    # Status and metadata
                    created_at=application_date,
                    updated_at=self.fake.date_time_between(start_date=application_date, end_date='now')
                )
                
                batch_applications.append(application)
                self.application_ids.append(application_id)
            
            self.bulk_insert("applications", batch_applications)
            applications.extend(batch_applications)
            print(f"  📋 Created batch {batch_start//batch_size + 1}: {len(batch_applications)} applications")
        
        print(f"  ✅ Created {len(applications)} FIES/ProUni applications")

    def seed_documents(self, count: int = 180000):
        """Create document submissions for applications (up to 22 per application)"""
        print(f"📎 Seeding {count} application documents...")
        
        documents = []
        batch_size = 2000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_documents = []
            
            for i in range(batch_start, batch_end):
                document_id = self.generate_id()
                application_id = random.choice(self.application_ids)
                
                # Choose document type with realistic distribution
                doc_type = random.choices(
                    list(self.document_types_info.keys()),
                    weights=[15, 15, 10, 12, 12, 20, 8, 15, 10, 12, 5],  # Higher weights for common docs (11 total)
                    k=1
                )[0]
                
                submission_date = self.fake.date_time_between(start_date='-1y', end_date='now')
                
                student_id = random.choice(self.student_ids)
                
                document = Document(
                    _id=document_id,
                    application_id=application_id,
                    student_id=student_id,  # Required field
                    
                    # Document details
                    document_type=DocumentType(doc_type),
                    document_name=f"{doc_type}_{application_id}.pdf",  # Required field (was file_name)
                    document_description=f"Student submitted {self.document_types_info[doc_type]}",
                    
                    # File information
                    file_path=f"/documents/applications/{application_id}/{doc_type}.pdf",
                    file_size=random.randint(100000, 5000000),  # 100KB to 5MB
                    file_format="pdf",  # Required field (was file_type)
                    mime_type="application/pdf",
                    checksum=f"sha256:{random.randint(100000000000000, 999999999999999):x}",  # Required field
                    
                    # Document metadata
                    upload_date=submission_date,  # Using upload_date from schema
                    version=1,
                    
                    # Verification process
                    status=random.choice(list(DocumentStatus)),
                    verification_date=self.fake.date_time_between(start_date=submission_date, end_date='now') if random.random() < 0.8 else None,
                    verified_by=random.choice(self.staff_ids) if len(self.staff_ids) > 0 else None,
                    
                    # Review information
                    review_notes=f"Document {doc_type} verification" if random.random() < 0.5 else None,
                    
                    # Document processing
                    ocr_extracted_text=f"Extracted text from {doc_type} document" if random.random() < 0.6 else None,
                    extracted_data={
                        "document_number": f"{random.randint(100000, 999999)}",
                        "issue_date": self.fake.date_between(start_date='-5y', end_date='today').isoformat(),
                        "validity": "valid"
                    } if random.random() < 0.7 else {},
                    validation_results={
                        "format_valid": True,
                        "content_readable": True,
                        "authenticity_check": "passed"
                    },
                    
                    # Security and compliance
                    digital_signature=f"signature_{random.randint(1000, 9999)}" if random.random() < 0.3 else None,
                    encryption_status=True,
                    
                    # Archive information
                    archived=False,
                    retention_period=7,  # 7 years retention
                    
                    # Status and timestamps
                    created_at=submission_date,
                    updated_at=self.fake.date_time_between(start_date=submission_date, end_date='now')
                )
                
                batch_documents.append(document)
            
            self.bulk_insert("documents", batch_documents)
            documents.extend(batch_documents)
            print(f"  📄 Created batch {batch_start//batch_size + 1}: {len(batch_documents)} documents")
        
        print(f"  ✅ Created {len(documents)} application documents")

    def seed_staff(self, count: int = 800):
        """Create Brazilian educational staff with diverse backgrounds"""
        print(f"👥 Seeding {count} educational staff members...")
        
        staff_members = []
        for i in range(count):
            staff_id = self.generate_id()
            
            # Generate diverse Brazilian names for staff
            first_name, last_name = self.fake.brazilian_full_name()
            
            # Staff role distribution
            role = random.choices(
                list(StaffRole), 
                weights=[15, 25, 20, 10, 15, 5, 5, 5],  # More teachers and administrators
                k=1
            )[0]
            
            staff_member = Staff(
                _id=staff_id,
                employee_id=f"FUNC{i+1:05d}",
                institution_id=random.choice(self.institution_ids),
                
                # Diverse Brazilian personal information
                first_name=first_name,
                last_name=last_name,
                full_name=f"{first_name} {last_name}",
                email=f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}@cogna.edu.br",
                
                # Brazilian identification
                cpf=self.fake.brazilian_cpf(),
                phone=self.fake.brazilian_phone(),
                
                # Professional details
                role=role,
                title=f"{role.value.replace('_', ' ').title()}",  # Convert enum to title
                department=random.choice([
                    "Administração Acadêmica", "Financeiro", "Recursos Humanos", "TI",
                    "Atendimento ao Aluno", "Coordenação de Curso", "Biblioteca",
                    "Secretaria Acadêmica", "Marketing", "Jurídico"
                ]),
                
                # Employment details
                hire_date=self.fake.date_time_between(start_date='-15y', end_date='-1m'),
                employment_type=random.choice(["full-time", "part-time", "contract"]),
                
                # Academic qualifications (common in Brazilian education) - simplified for schema
                areas_of_expertise=random.sample([
                    "Educação", "Administração Educacional", "Psicologia Educacional",
                    "Tecnologia Educacional", "Gestão de Projetos", "Qualidade em Educação"
                ], k=random.randint(1, 3)),
                
                # Work assignment and capacity - simplified for schema
                workload_percentage=random.randint(50, 100),
                maximum_applications=random.randint(10, 50) if role in [StaffRole.ADMINISTRATOR, StaffRole.ADMISSIONS_OFFICER] else None,
                
                # Status
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            staff_members.append(staff_member)
            self.staff_ids.append(staff_id)
        
        self.bulk_insert("staff", staff_members)
        print(f"  ✅ Created {len(staff_members)} staff members with diverse Brazilian backgrounds")

    def seed_programs(self, count: int = 100):
        """Create Brazilian academic programs"""
        print(f"🎯 Seeding {count} academic programs...")
        
        self.program_ids = []
        programs = []
        
        for i in range(count):
            program_id = self.generate_id()
            
            program_name = self.fake.academic_program()
            institution_id = random.choice(self.institution_ids)
            
            program = Program(
                _id=program_id,
                institution_id=institution_id,
                
                # Program identification
                name=program_name,
                program_code=f"PROG{i+1:04d}",
                mec_code=f"MEC{random.randint(100000, 999999)}",
                
                # Program details
                degree_level=random.choice(["undergraduate", "graduate", "doctoral"]),
                degree_type=random.choice(["Bacharel", "Licenciatura", "Tecnólogo", "Mestrado", "Doutorado"]),
                field_of_study=program_name,
                specialization=f"Especialização em {program_name}" if random.random() < 0.3 else None,
                
                # Required fields
                description=f"Programa de {program_name} - formação completa e qualificada para o mercado brasileiro",
                tuition_per_semester=random.uniform(800.0, 5000.0),  # BRL tuition cost
                accreditation_status=random.choice(["accredited", "provisional", "under_review"]),
                max_enrollment=random.randint(50, 300),
                start_date=self.fake.date_time_between(start_date='-5y', end_date='now'),
                
                # Academic structure
                total_credits=random.randint(120, 300),
                duration_semesters=random.randint(8, 12),
                modality=random.choice(["On-site", "Online", "Hybrid"]),
                
                # Additional information
                career_outcomes=[
                    f"Profissional de {program_name}",
                    f"Especialista em {program_name}",
                    f"Consultor de {program_name}"
                ],
                current_enrollment=random.randint(20, 250),
                completion_rate=random.uniform(0.70, 0.95),
                employment_rate=random.uniform(0.75, 0.90),
                
                # Status
                is_active=True,
                
                # Metadata
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            programs.append(program)
            self.program_ids.append(program_id)
        
        self.bulk_insert("programs", programs)
        print(f"  ✅ Created {len(programs)} academic programs")

    def seed_courses(self, count: int = 800):
        """Create Brazilian academic courses and programs"""
        print(f"📚 Seeding {count} academic courses...")
        
        courses = []
        for i in range(count):
            course_id = self.generate_id()
            
            program_name = self.fake.academic_program()
            institution_id = random.choice(self.institution_ids)
            
            # Generate required IDs
            program_id = random.choice(self.program_ids) if hasattr(self, 'program_ids') and self.program_ids else self.generate_id()
            primary_instructor = random.choice(self.staff_ids) if self.staff_ids else self.generate_id()
            
            course = Course(
                _id=course_id,
                course_code=f"CURSO{i+1:04d}",
                institution_id=institution_id,
                program_id=program_id,
                
                # Required fields from schema
                name=program_name,  # Required field
                level=random.choice(["graduação", "pós-graduação", "mestrado", "doutorado"]),  # Required field
                subject_area=program_name,  # Required field
                total_hours=random.randint(60, 240),  # Required field
                modality=random.choice(["presencial", "ead", "hibrido"]),  # Required field
                primary_instructor=primary_instructor,  # Required field
                max_enrollment=random.randint(50, 200),  # Required field
                semester=random.choice(["2024/1", "2024/2"]),  # Required field
                
                # Course content
                description=f"Curso de {program_name} - formação profissional completa",
                prerequisites=random.sample([f"CURSO{j:04d}" for j in range(1, i)], k=random.randint(0, 3)) if i > 10 else [],
                learning_objectives=[
                    f"Desenvolver competências em {program_name}",
                    f"Aplicar conhecimentos teóricos e práticos", 
                    f"Preparar para o mercado de trabalho brasileiro"
                ],
                
                # Academic structure
                credits=random.randint(2, 8),
                lecture_hours=random.randint(30, 120),
                lab_hours=random.randint(0, 60),
                seminar_hours=random.randint(0, 30),
                
                # Schedule (Brazilian format)
                schedule={
                    "days": random.sample(["segunda", "terça", "quarta", "quinta", "sexta", "sábado"], k=random.randint(1, 3)),
                    "start_time": f"{random.randint(7, 19):02d}:{random.choice(['00', '30'])}",
                    "end_time": f"{random.randint(8, 22):02d}:{random.choice(['00', '30'])}",
                    "classroom": f"Sala {random.randint(101, 999)}"
                },
                
                # Assessment and grading (as list of dicts as per schema)
                assessment_methods=[
                    {"type": "provas", "weight": 0.4, "description": "Avaliações escritas"},
                    {"type": "trabalhos", "weight": 0.3, "description": "Projetos e trabalhos"},
                    {"type": "participação", "weight": 0.3, "description": "Participação em aula"}
                ],
                
                # Course materials and resources
                reading_list=[
                    {"title": f"Livro de {program_name} - Volume 1", "author": "Autor Brasileiro", "required": True},
                    {"title": f"Manual de {program_name} - Edição Brasileira", "author": "Especialista", "required": False}
                ],
                
                # Enrollment information
                current_enrollment=random.randint(20, 150),
                waitlist_size=random.randint(0, 20),
                
                # Status and metrics
                status=random.choice(list(CourseStatus)),
                academic_year=random.randint(2020, 2024),
                completion_rate=random.uniform(0.75, 0.95),
                average_grade=random.uniform(6.0, 9.0),
                student_satisfaction=random.uniform(7.0, 10.0),
                
                # Metadata
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            courses.append(course)
            self.course_ids.append(course_id)
        
        self.bulk_insert("courses", courses)
        print(f"  ✅ Created {len(courses)} Brazilian academic courses")

    def seed_enrollments(self, count: int = 25000):
        """Create student course enrollments"""
        print(f"🎓 Seeding {count} course enrollments...")
        
        enrollments = []
        batch_size = 1000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_enrollments = []
            
            for i in range(batch_start, batch_end):
                enrollment_id = self.generate_id()
                
                enrollment_date = self.fake.date_time_between(start_date='-2y', end_date='now')
                
                enrollment = Enrollment(
                    _id=enrollment_id,
                    student_id=random.choice(self.student_ids),
                    course_id=random.choice(self.course_ids),
                    
                    # Enrollment details
                    enrollment_date=enrollment_date,
                    semester=f"{enrollment_date.year}/{1 if enrollment_date.month <= 6 else 2}",
                    academic_year=enrollment_date.year,
                    
                    # Status and performance
                    status=random.choice(list(EnrollmentStatus)),
                    current_grade=random.uniform(4.0, 10.0),  # Brazilian 0-10 scale
                    attendance_percentage=random.uniform(0.6, 1.0),
                    
                    # Progress tracking
                    assignments_completed=random.randint(0, 15),
                    assignments_total=random.randint(10, 20),
                    exams_taken=random.randint(0, 4),
                    participation_score=random.uniform(6.0, 10.0),
                    
                    # Financial information
                    tuition_amount=random.uniform(800, 3000),  # Monthly tuition in BRL
                    payment_status=random.choice(["paid", "pending", "overdue", "financial_aid"]),
                    
                    # Completion details
                    completion_date=enrollment_date + timedelta(days=random.randint(120, 180)) if random.random() < 0.7 else None,
                    final_grade=random.uniform(6.0, 10.0) if random.random() < 0.8 else None,
                    passed=random.choice([True, False]),
                    
                    # Metadata
                    created_at=enrollment_date,
                    updated_at=self.fake.date_time_between(start_date=enrollment_date, end_date='now')
                )
                
                batch_enrollments.append(enrollment)
                if not hasattr(self, 'enrollment_ids'):
                    self.enrollment_ids = []
                self.enrollment_ids.append(enrollment_id)
            
            self.bulk_insert("enrollments", batch_enrollments)
            enrollments.extend(batch_enrollments)
            print(f"  📖 Created batch {batch_start//batch_size + 1}: {len(batch_enrollments)} enrollments")
        
        print(f"  ✅ Created {len(enrollments)} course enrollments")

    def seed_assessments(self, count: int = 50000):
        """Create student assessments and assignments"""
        print(f"📝 Seeding {count} assessments and assignments...")
        
        assessments = []
        batch_size = 2000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_assessments = []
            
            for i in range(batch_start, batch_end):
                assessment_id = self.generate_id()
                
                # Assessment timing
                due_date = self.fake.date_time_between(start_date='-1y', end_date='+3m')
                created_date = due_date - timedelta(days=random.randint(7, 30))
                
                assessment_type = random.choice(list(AssessmentType))
                
                # Brazilian assessment names based on type
                assessment_names = {
                    "assignment": ["Trabalho de Pesquisa", "Projeto Prático", "Estudo de Caso", "Relatório"],
                    "exam": ["Prova Bimestral", "Exame Final", "Avaliação Integrada", "Prova Substitutiva"],
                    "project": ["Projeto Final", "TCC", "Projeto Integrador", "Trabalho de Conclusão"],
                    "presentation": ["Apresentação Oral", "Seminário", "Defesa do Projeto", "Exposição"],
                    "participation": ["Participação em Aula", "Discussão em Grupo", "Atividade Colaborativa", "Engajamento"],
                    "final_exam": ["Exame Final", "Prova Final", "Avaliação Final Integrada", "Prova de Segunda Chamada"]
                }
                
                # Calculate scores
                points_earned = random.uniform(4.0, 10.0) if random.random() < 0.85 else 0.0
                points_possible = 10.0
                percentage_score = (points_earned / points_possible) if points_possible > 0 else 0  # Decimal 0-1, not percentage
                
                assessment = Assessment(
                    _id=assessment_id,
                    student_id=random.choice(self.student_ids),
                    course_id=random.choice(self.course_ids),
                    enrollment_id=random.choice(self.enrollment_ids) if hasattr(self, 'enrollment_ids') and self.enrollment_ids else self.generate_id(),  # Required field
                    
                    # Assessment details
                    title=random.choice(assessment_names[assessment_type.value]),
                    assessment_type=assessment_type,  # Changed from 'type' to 'assessment_type'
                    description=f"Avaliação de {assessment_type.value} para verificação do aprendizado",
                    
                    # Scheduling
                    due_date=due_date,
                    submission_date=self.fake.date_time_between(start_date=due_date - timedelta(days=7), end_date=due_date + timedelta(days=2)) if random.random() < 0.9 else None,
                    
                    # Grading (Brazilian 0-10 scale)
                    points_possible=points_possible,
                    points_earned=points_earned,
                    percentage_score=percentage_score,  # Fixed lambda function issue
                    weight_percentage=random.uniform(0.1, 0.5),  # Required field (decimal 0-1, not percentage)
                    letter_grade=None,  # Brazilian system typically uses numerical grades
                    
                    # Feedback and rubric
                    instructor_feedback=random.choice([
                        "Bom trabalho, continue assim!",
                        "Necessita melhorar a argumentação",
                        "Excelente análise e apresentação",
                        "Cumpriu os requisitos mínimos",
                        "Superou as expectativas"
                    ]) if random.random() < 0.7 else "",
                    
                    # Submission details
                    submission_method=random.choice(["online_upload", "physical_submission", "oral_presentation"]),
                    file_attachments=random.randint(0, 5),
                    
                    # Status tracking
                    is_submitted=random.choice([True, False]),
                    is_graded=random.choice([True, False]),
                    is_late=random.choice([True, False]),
                    attempts_allowed=random.randint(1, 3),
                    attempts_used=random.randint(1, 2),
                    
                    # Metadata
                    created_at=created_date,
                    updated_at=self.fake.date_time_between(start_date=created_date, end_date='now')
                )
                
                batch_assessments.append(assessment)
            
            self.bulk_insert("assessments", batch_assessments)
            assessments.extend(batch_assessments)
            print(f"  ✏️  Created batch {batch_start//batch_size + 1}: {len(batch_assessments)} assessments")
        
        print(f"  ✅ Created {len(assessments)} assessments with Brazilian naming patterns")

    def seed_content(self, count: int = 3000):
        """Create learning content and materials"""
        print(f"📖 Seeding {count} learning content items...")
        
        content_items = []
        for i in range(count):
            content_id = self.generate_id()
            
            content_types = ["video", "document", "presentation", "quiz", "assignment", "reading"]
            content_type = random.choice(content_types)
            course_id = random.choice(self.course_ids)
            
            # Brazilian content titles based on type
            content_titles = {
                "reading": ["Leitura Obrigatória", "Texto Complementar", "Artigo Científico", "Material de Apoio"],
                "video": ["Vídeo-aula", "Tutorial Prático", "Demonstração", "Palestra Gravada"],
                "assignment": ["Exercícios Práticos", "Lista de Exercícios", "Atividade Avaliativa", "Tarefa Individual"],
                "quiz": ["Quiz Interativo", "Auto-avaliação", "Teste de Conhecimento", "Revisão Rápida"],
                "document": ["Documento PDF", "Apostila", "Manual", "Guia de Estudos"],  # Added missing key
                "presentation": ["Apresentação", "Slides", "Seminário", "Exposição Visual"]  # Added missing key
            }
            
            content = Content(
                _id=content_id,
                course_id=course_id,
                
                # Content details
                title=f"{random.choice(content_titles[content_type])} - Módulo {random.randint(1, 12)}",
                content_type=content_type,
                category=random.choice(["lecture", "assignment", "reading", "discussion", "assessment"]),
                description=f"Material de {content_type} para aprofundamento do conhecimento",
                
                # Educational metadata
                difficulty_level=random.choice(["beginner", "intermediate", "advanced"]),
                estimated_time=random.randint(15, 180),
                
                # File information
                file_path=f"/content/{course_id}/{content_type}_{i+1}",
                file_size=random.randint(1000000, 50000000),  # 1MB to 50MB
                file_format=random.choice(["pdf", "mp4", "html", "pptx"]),
                mime_type=random.choice(["application/pdf", "video/mp4", "text/html", "application/vnd.ms-powerpoint"]),
                
                # Access and permissions  
                visibility=random.choice(["public", "institution", "course", "private"]),
                prerequisites=[],  # Simplified for seeding
                
                # Interaction metrics
                view_count=random.randint(0, 1000),
                download_count=random.randint(0, 500),
                average_rating=random.uniform(3.5, 5.0),
                
                # Content metadata  
                keywords=random.sample([
                    "educação", "aprendizagem", "brasil", "ensino superior", 
                    "conteúdo educacional", "material didático"
                ], k=random.randint(2, 4)),
                
                # Publishing details
                author=random.choice(self.staff_ids) if self.staff_ids else self.generate_id(),
                institution_id=random.choice(self.institution_ids),
                is_published=random.choice([True, False]),
                
                # Status
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            content_items.append(content)
        
        self.bulk_insert("content", content_items)
        print(f"  ✅ Created {len(content_items)} learning content items")

    def seed_financial_aid(self, count: int = 8000):
        """Create financial aid and scholarship records"""
        print(f"💰 Seeding {count} financial aid records...")
        
        financial_aid_records = []
        batch_size = 1000
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                aid_id = self.generate_id()
                student_id = random.choice(self.student_ids)
                
                # Aid program selection with realistic distribution
                program, program_description = random.choices(
                    self.funding_programs,
                    weights=[40, 35, 10, 10, 5],  # Higher weights for FIES/ProUni
                    k=1
                )[0]
                
                award_date = self.fake.date_time_between(start_date='-2y', end_date='now')
                
                award_amount = random.uniform(5000, 50000)  # Annual amount
                disbursed_amount = random.uniform(2000, min(45000, award_amount))
                remaining_amount = max(0, award_amount - disbursed_amount)
                
                financial_aid = FinancialAid(
                    _id=aid_id,
                    student_id=student_id,
                    institution_id=random.choice(self.institution_ids),
                    application_id=random.choice(self.application_ids) if random.random() < 0.8 else None,
                    
                    # Required fields
                    aid_id=f"AID{i+1:08d}",  # Required field
                    funding_program=FundingProgram(program.lower()),  # Required field (enum)
                    aid_type=random.choice(["scholarship", "loan", "grant", "work_study"]),  # Required field
                    award_amount=award_amount,  # Required field
                    remaining_amount=remaining_amount,  # Required field
                    academic_year=random.randint(2020, 2024),  # Required field
                    start_date=award_date,  # Required field
                    end_date=award_date + timedelta(days=random.randint(365, 2190)),  # Required field (1-6 years)
                    status=random.choice(["active", "suspended", "completed", "cancelled"]),  # Required field
                    
                    # Optional fields that exist in schema
                    disbursed_amount=disbursed_amount,
                    semester=random.choice(["2024/1", "2024/2"]),
                    gpa_requirement=random.uniform(6.0, 8.0),  # Brazilian scale
                    credit_hour_requirement=random.randint(120, 240),
                    status_reason="Aid program requirements met" if random.random() < 0.8 else "Under review",
                    government_approval_number=f"{program}_{random.randint(100000, 999999)}" if program in ["FIES", "ProUni"] else None,
                    government_status="approved" if random.random() < 0.8 else "pending",
                    fies_contract_number=f"FIES_{random.randint(100000000, 999999999)}" if program == "FIES" else None,
                    
                    # Metadata
                    created_at=award_date,
                    updated_at=self.fake.date_time_between(start_date=award_date, end_date='now')
                )
                
                batch_records.append(financial_aid)
            
            self.bulk_insert("financial_aid", batch_records)
            financial_aid_records.extend(batch_records)
            print(f"  💳 Created batch {batch_start//batch_size + 1}: {len(batch_records)} aid records")
        
        print(f"  ✅ Created {len(financial_aid_records)} financial aid records")

    def run_seeding(self):
        """Execute the complete Brazilian EdTech database seeding process"""
        print("🇧🇷 COGNA EDUCAÇÃO - BRAZILIAN EDTECH PLATFORM")
        print("=" * 60)
        print("🌱 Seeding database with diverse Brazilian educational data...")
        print("  • Diverse Brazilian naming patterns (Portuguese, Italian, German, Japanese, African, Indigenous, Lebanese)")
        print("  • Government funding programs (FIES, ProUni, CAPES, CNPq)")
        print("  • Multi-institutional academic system")
        print("  • Document verification workflows (up to 22 documents per application)")
        print("  • Brazilian academic standards and compliance")
        print()
        
        start_time = datetime.utcnow()
        
        # Seed data in dependency order
        self.seed_institutions(12)
        self.seed_staff(800)
        self.seed_programs(100)  # Create programs before courses
        self.seed_students(5000)
        self.seed_courses(800)
        self.seed_applications(15000)
        self.seed_documents(180000)  # Up to 22 documents per application
        self.seed_enrollments(25000)
        self.seed_assessments(50000)
        self.seed_content(3000)
        self.seed_financial_aid(8000)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate total documents seeded
        total_documents = 12 + 800 + 100 + 5000 + 800 + 15000 + 180000 + 25000 + 50000 + 3000 + 8000
        
        print()
        print("🎓 BRAZILIAN EDTECH DATABASE SEEDING COMPLETED!")
        print("=" * 60)
        print(f"  📊 Total documents created: {total_documents:,}")
        print(f"  ⏱️  Seeding completed in {duration:.1f} seconds")
        print(f"  🏫 Educational institutions: 12")
        print(f"  👨‍🎓 Students with diverse Brazilian names: 5,000")
        print(f"  📄 FIES/ProUni applications: 15,000") 
        print(f"  📎 Application documents: 180,000")
        print(f"  👥 Staff members: 800")
        print(f"  📚 Academic courses: 800")
        print(f"  🎓 Course enrollments: 25,000")
        print(f"  📝 Assessments and assignments: 50,000")
        print(f"  📖 Learning content items: 3,000")
        print(f"  💰 Financial aid records: 8,000")
        print()
        print("🇧🇷 Ready to serve 2.4 million Brazilian students with diverse cultural backgrounds!")
        
        return {
            "total_documents": total_documents,
            "duration_seconds": duration,
            "collections_created": 11,
            "institutions": 12,
            "students": 5000,
            "applications": 15000,
            "documents": 180000,
            "staff": 800,
            "courses": 800,
            "enrollments": 25000,
            "assessments": 50000,
            "content": 3000,
            "financial_aid": 8000
        }

    # Abstract methods implementation
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with the specified number of records"""
        return self.run_seeding()
    
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        # Indexes are created automatically when creating database schema
        pass
    
    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        from pymongo import MongoClient
        client = MongoClient(self.connection_string)
        db = client[self.database_schema.database_name]
        # Drop all collections
        for collection_name in db.list_collection_names():
            db[collection_name].drop()
        client.close()
    
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        from pymongo import MongoClient
        client = MongoClient(self.connection_string)
        db = client[self.database_schema.database_name]
        
        # Basic validation - check that collections have data
        for collection_name in self.database_schema.collections.keys():
            count = db[collection_name].count_documents({})
            if count == 0:
                raise ValueError(f"Collection '{collection_name}' is empty after seeding")
        
        client.close()
        return True


# Export the seeder class  
seeder = BrazilianEdTechSeeder()