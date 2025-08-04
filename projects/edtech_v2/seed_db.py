"""
Brazilian EdTech Platform - Database Seeder
Generates realistic sample data for the brazilian_edtech database
"""

from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from bson import ObjectId
from typing import Dict, Optional, List, Tuple
# from decimal import Decimal  # MongoDB doesn't support Decimal, using float instead
import hashlib
from collections import defaultdict
import logging

# Import the abstract base class and schema
from mimoid.seeder_base import DatabaseSeeder
from mimoid.schema_types import PyObjectId, IndexDirection
from db_schema import (
    BrazilianEdtechSchema,
    UserRole, ApplicationStatus, DocumentType, FundingProgramType,
    InstitutionType, WorkflowStage,
    User, Student, Application, Document, Protocol, FundingProgram,
    Institution, Workflow, Notification, AuditLog, ApplicationStats,
    ArchivedDocument
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Brazilian states and major cities
BRAZILIAN_STATES = {
    'SP': {'name': 'São Paulo', 'cities': ['São Paulo', 'Campinas', 'Santos', 'São José dos Campos', 'Ribeirão Preto', 'Sorocaba']},
    'RJ': {'name': 'Rio de Janeiro', 'cities': ['Rio de Janeiro', 'Niterói', 'Nova Iguaçu', 'Duque de Caxias', 'São Gonçalo']},
    'MG': {'name': 'Minas Gerais', 'cities': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim']},
    'BA': {'name': 'Bahia', 'cities': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari']},
    'RS': {'name': 'Rio Grande do Sul', 'cities': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Santa Maria']},
    'PR': {'name': 'Paraná', 'cities': ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel']},
    'PE': {'name': 'Pernambuco', 'cities': ['Recife', 'Olinda', 'Jaboatão dos Guararapes', 'Caruaru']},
    'CE': {'name': 'Ceará', 'cities': ['Fortaleza', 'Caucaia', 'Juazeiro do Norte', 'Maracanaú']},
    'PA': {'name': 'Pará', 'cities': ['Belém', 'Ananindeua', 'Santarém', 'Marabá']},
    'SC': {'name': 'Santa Catarina', 'cities': ['Florianópolis', 'Joinville', 'Blumenau', 'São José']},
    'GO': {'name': 'Goiás', 'cities': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde']},
    'DF': {'name': 'Distrito Federal', 'cities': ['Brasília', 'Taguatinga', 'Ceilândia', 'Águas Claras']},
}

# Common Brazilian neighborhoods by city
NEIGHBORHOODS = {
    'São Paulo': ['Vila Mariana', 'Pinheiros', 'Moema', 'Perdizes', 'Tatuapé', 'Santana', 'Santo Amaro', 'Mooca'],
    'Rio de Janeiro': ['Copacabana', 'Ipanema', 'Leblon', 'Botafogo', 'Tijuca', 'Barra da Tijuca', 'Flamengo'],
    'Belo Horizonte': ['Savassi', 'Lourdes', 'Funcionários', 'Buritis', 'Belvedere', 'Santo Antônio'],
    'Salvador': ['Pituba', 'Barra', 'Graça', 'Rio Vermelho', 'Ondina', 'Itapuã'],
    'Curitiba': ['Batel', 'Centro', 'Água Verde', 'Bigorrilho', 'Mercês', 'Champagnat'],
    'Porto Alegre': ['Moinhos de Vento', 'Cidade Baixa', 'Menino Deus', 'Petrópolis', 'Bela Vista'],
    'Recife': ['Boa Viagem', 'Casa Forte', 'Graças', 'Espinheiro', 'Parnamirim'],
    'Fortaleza': ['Aldeota', 'Meireles', 'Varjota', 'Papicu', 'Cocó'],
    'Brasília': ['Asa Sul', 'Asa Norte', 'Lago Sul', 'Lago Norte', 'Sudoeste']
}

# Course names by degree type
COURSES = {
    'bachelor': [
        'Administração', 'Direito', 'Engenharia Civil', 'Engenharia de Software', 
        'Medicina', 'Psicologia', 'Pedagogia', 'Ciências Contábeis', 'Arquitetura',
        'Enfermagem', 'Fisioterapia', 'Nutrição', 'Odontologia', 'Farmácia',
        'Comunicação Social', 'Publicidade e Propaganda', 'Jornalismo', 'Economia',
        'Sistemas de Informação', 'Ciência da Computação', 'Engenharia Elétrica'
    ],
    'technologist': [
        'Análise e Desenvolvimento de Sistemas', 'Gestão de Recursos Humanos',
        'Marketing Digital', 'Logística', 'Gestão Financeira', 'Redes de Computadores',
        'Segurança da Informação', 'Design Gráfico', 'Gastronomia', 'Estética e Cosmética'
    ],
    'postgraduate': [
        'MBA em Gestão Empresarial', 'MBA em Marketing', 'MBA em Finanças',
        'Especialização em Direito Tributário', 'Especialização em Psicologia Clínica',
        'Especialização em Engenharia de Software', 'MBA em Gestão de Projetos'
    ]
}


class BrazilianEdtechSeeder(DatabaseSeeder):
    """Concrete implementation of DatabaseSeeder for Brazilian EdTech platform"""
    
    def __init__(self, connection_string: str, database_schema: BrazilianEdtechSchema):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker('pt_BR')  # Use Brazilian Portuguese locale
        
        # Cache for referential integrity
        self.user_ids = []
        self.student_ids = []
        self.institution_ids = []
        self.funding_program_ids = []
        self.application_ids = []
        self.workflow_ids = []
        
        # Mapping caches
        self.cpf_to_user = {}
        self.user_to_student = {}
    
    def _convert_enums_to_values(self, obj):
        """Recursively convert all enum values to their string/value representation"""
        if isinstance(obj, dict):
            return {k: self._convert_enums_to_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_enums_to_values(item) for item in obj]
        elif hasattr(obj, 'value'):  # It's an enum
            return obj.value
        else:
            return obj
        
    def generate_cpf(self) -> str:
        """Generate a valid Brazilian CPF number"""
        # Generate 9 random digits
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calculate first verification digit
        sum1 = sum((10 - i) * cpf[i] for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        cpf.append(digit1)
        
        # Calculate second verification digit
        sum2 = sum((11 - i) * cpf[i] for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        cpf.append(digit2)
        
        return ''.join(map(str, cpf))
    
    def generate_cnpj(self) -> str:
        """Generate a valid Brazilian CNPJ number"""
        # Generate 12 random digits
        cnpj = [random.randint(0, 9) for _ in range(8)]
        cnpj.extend([0, 0, 0, 1])  # Standard suffix for main establishment
        
        # Calculate verification digits
        sequence = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = sum(cnpj[i] * sequence[i] for i in range(12))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        cnpj.append(digit1)
        
        sequence = [6] + sequence
        sum2 = sum(cnpj[i] * sequence[i] for i in range(13))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        cnpj.append(digit2)
        
        return ''.join(map(str, cnpj))
    
    def generate_brazilian_phone(self) -> str:
        """Generate a valid Brazilian phone number"""
        # Area codes for major cities
        area_codes = ['11', '21', '31', '41', '51', '61', '71', '81', '85']
        area_code = random.choice(area_codes)
        
        # Mobile numbers start with 9
        number = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        return f"({area_code}) {number}"
    
    def generate_zip_code(self, state: str, city: str) -> str:
        """Generate a valid Brazilian ZIP code for the given location"""
        # Brazilian ZIP codes by region (first 2 digits)
        state_prefixes = {
            'SP': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'],
            'RJ': ['20', '21', '22', '23', '24', '25', '26', '27', '28'],
            'MG': ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39'],
            'BA': ['40', '41', '42', '43', '44', '45', '46', '47', '48'],
            'PE': ['50', '51', '52', '53', '54', '55', '56'],
            'CE': ['60', '61', '62', '63'],
            'DF': ['70', '71', '72'],
            'GO': ['74', '75', '76'],
            'PR': ['80', '81', '82', '83', '84', '85', '86', '87'],
            'SC': ['88', '89'],
            'RS': ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99'],
            'PA': ['66', '67', '68']
        }
        
        prefix = random.choice(state_prefixes.get(state, ['01']))
        suffix = f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}"
        
        return f"{prefix}{suffix}"
    
    def generate_mec_code(self) -> str:
        """Generate a valid MEC (Ministry of Education) code"""
        return f"{random.randint(1000, 9999)}"
    
    def generate_protocol_number(self, year: int, month: int) -> str:
        """Generate a protocol number in format YYYYMM-XXXXXX"""
        sequence = random.randint(100000, 999999)
        return f"{year}{month:02d}-{sequence}"
    
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            # Default numbers based on requirements
            num_records = {
                'institutions': 150,  # Various educational institutions
                'funding_programs': 10,  # FIES, ProUni, and others
                'users': 5000,  # Mix of students, staff, reviewers
                'students': 3000,  # Active students
                'applications': 57000,  # Per semester requirement
                'documents': 1254000,  # 22 per application average
                'workflows': 20,  # Different workflow configurations
                'notifications': 100000,  # Various notifications
                'audit_logs': 200000  # Audit trail
            }
        
        logger.info("Starting database seeding...")
        
        # Seed in dependency order
        logger.info(f"Seeding {num_records['institutions']} institutions...")
        self.seed_institutions(num_records['institutions'])
        
        logger.info(f"Seeding {num_records['funding_programs']} funding programs...")
        self.seed_funding_programs(num_records['funding_programs'])
        
        logger.info(f"Seeding {num_records['workflows']} workflows...")
        self.seed_workflows(num_records['workflows'])
        
        logger.info(f"Seeding {num_records['users']} users...")
        self.seed_users(num_records['users'])
        
        logger.info(f"Seeding {num_records['students']} students...")
        self.seed_students(num_records['students'])
        
        logger.info(f"Seeding {num_records['applications']} applications...")
        self.seed_applications(num_records['applications'])
        
        logger.info(f"Seeding {num_records['documents']} documents...")
        self.seed_documents(num_records['documents'])
        
        logger.info("Seeding protocols for all applications...")
        self.seed_protocols()
        
        logger.info(f"Seeding {num_records['notifications']} notifications...")
        self.seed_notifications(num_records['notifications'])
        
        logger.info(f"Seeding {num_records['audit_logs']} audit logs...")
        self.seed_audit_logs(num_records['audit_logs'])
        
        logger.info("Generating application statistics...")
        self.generate_application_stats()
        
        logger.info("Database seeding completed!")
    
    def seed_institutions(self, count: int):
        """Generate and insert institution documents"""
        logger.info(f"Starting to generate {count} institutions...")
        institutions = []
        used_cnpjs = set()
        used_mec_codes = set()
        
        # Famous Brazilian universities
        famous_institutions = [
            {'name': 'Universidade de São Paulo', 'type': InstitutionType.UNIVERSITY, 'state': 'SP', 'city': 'São Paulo'},
            {'name': 'Universidade Federal do Rio de Janeiro', 'type': InstitutionType.UNIVERSITY, 'state': 'RJ', 'city': 'Rio de Janeiro'},
            {'name': 'Universidade Federal de Minas Gerais', 'type': InstitutionType.UNIVERSITY, 'state': 'MG', 'city': 'Belo Horizonte'},
            {'name': 'Pontifícia Universidade Católica de São Paulo', 'type': InstitutionType.UNIVERSITY, 'state': 'SP', 'city': 'São Paulo'},
            {'name': 'Universidade Federal da Bahia', 'type': InstitutionType.UNIVERSITY, 'state': 'BA', 'city': 'Salvador'},
            {'name': 'Universidade Federal do Rio Grande do Sul', 'type': InstitutionType.UNIVERSITY, 'state': 'RS', 'city': 'Porto Alegre'},
            {'name': 'Universidade de Brasília', 'type': InstitutionType.UNIVERSITY, 'state': 'DF', 'city': 'Brasília'},
            {'name': 'Universidade Federal de Pernambuco', 'type': InstitutionType.UNIVERSITY, 'state': 'PE', 'city': 'Recife'},
        ]
        
        # Add famous institutions first
        for i, inst_data in enumerate(famous_institutions[:min(len(famous_institutions), count)]):
            logger.debug(f"Generating institution {i+1}/{count}: {inst_data['name']}")
            cnpj = self.generate_cnpj()
            while cnpj in used_cnpjs:
                cnpj = self.generate_cnpj()
            used_cnpjs.add(cnpj)
            
            mec_code = self.generate_mec_code()
            while mec_code in used_mec_codes:
                mec_code = self.generate_mec_code()
            used_mec_codes.add(mec_code)
            
            # Generate courses (simplified for performance)
            courses = []
            # Universities have more diverse courses
            if inst_data['type'] == InstitutionType.UNIVERSITY:
                num_courses = random.randint(10, 20)  # Reduced from 15-30
                course_types = ['bachelor', 'postgraduate']
            else:
                num_courses = random.randint(5, 10)  # Reduced from 5-15
                course_types = ['technologist', 'bachelor']
            
            # Pre-select course names to avoid repeated random choices
            selected_courses = []
            for course_type in course_types:
                selected_courses.extend(random.sample(COURSES[course_type], min(num_courses//len(course_types), len(COURSES[course_type]))))
            
            for course_name in selected_courses[:num_courses]:
                course_type = 'bachelor' if course_name in COURSES['bachelor'] else ('technologist' if course_name in COURSES['technologist'] else 'postgraduate')
                
                duration = {
                    'bachelor': random.choice([8, 10, 12]),  # 4-6 years
                    'technologist': random.choice([4, 5, 6]),  # 2-3 years
                    'postgraduate': random.choice([2, 3, 4])  # 1-2 years
                }[course_type]
                
                monthly_fee = float(random.randint(800, 5000))
                
                courses.append({
                    'name': course_name,
                    'degree_type': course_type,
                    'duration_semesters': duration,
                    'monthly_fee': monthly_fee,
                    'is_active': random.random() < 0.95
                })
            
            # Get neighborhoods for the city
            neighborhoods = NEIGHBORHOODS.get(inst_data['city'], ['Centro', 'Jardim América', 'Vila Nova'])
            
            institution = {
                '_id': ObjectId(),
                'name': inst_data['name'],
                'institution_type': inst_data['type'].value,
                'cnpj': cnpj,
                'mec_code': mec_code,
                'address': {
                    'street': self.fake.street_name(),
                    'number': str(random.randint(1, 9999)),
                    'complement': random.choice(['', 'Bloco A', 'Prédio Principal', 'Campus I']),
                    'neighborhood': random.choice(neighborhoods),
                    'city': inst_data['city'],
                    'state': inst_data['state'],
                    'zip_code': self.generate_zip_code(inst_data['state'], inst_data['city']),
                    'latitude': float(self.fake.latitude()),
                    'longitude': float(self.fake.longitude())
                },
                'courses': courses,
                'total_students': random.randint(1000, 15000),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'accepts_fies': True,
                'accepts_prouni': True,
                'created_at': self.fake.date_time_between(start_date='-5y', end_date='-1y'),
                'updated_at': datetime.utcnow()
            }
            
            institutions.append(institution)
        
        # Generate remaining institutions
        remaining = count - len(institutions)
        institution_types = [
            (InstitutionType.COLLEGE, 0.4),
            (InstitutionType.UNIVERSITY, 0.2),
            (InstitutionType.TECHNICAL_SCHOOL, 0.2),
            (InstitutionType.DISTANCE_LEARNING, 0.15),
            (InstitutionType.POSTGRADUATE, 0.05)
        ]
        
        logger.info(f"Generating {remaining} additional institutions...")
        for idx in range(remaining):
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{remaining} institutions generated...")
            # Choose random state and city
            state = random.choice(list(BRAZILIAN_STATES.keys()))
            city = random.choice(BRAZILIAN_STATES[state]['cities'])
            
            cnpj = self.generate_cnpj()
            while cnpj in used_cnpjs:
                cnpj = self.generate_cnpj()
            used_cnpjs.add(cnpj)
            
            mec_code = self.generate_mec_code()
            while mec_code in used_mec_codes:
                mec_code = self.generate_mec_code()
            used_mec_codes.add(mec_code)
            
            # Choose institution type with weights
            inst_type = random.choices(
                [t[0] for t in institution_types],
                weights=[t[1] for t in institution_types]
            )[0]
            
            # Generate name based on type
            name_patterns = {
                InstitutionType.UNIVERSITY: [
                    f"Universidade {random.choice(['Federal', 'Estadual', 'Católica', 'Metodista'])} de {city}",
                    f"Universidade {self.fake.last_name()}",
                    f"Centro Universitário {self.fake.last_name()}"
                ],
                InstitutionType.COLLEGE: [
                    f"Faculdade {self.fake.last_name()}",
                    f"Faculdade de {random.choice(['Tecnologia', 'Ciências', 'Negócios'])} {city}",
                    f"Instituto Superior de {random.choice(['Educação', 'Tecnologia', 'Gestão'])}"
                ],
                InstitutionType.TECHNICAL_SCHOOL: [
                    f"Instituto Federal de {BRAZILIAN_STATES[state]['name']}",
                    f"Escola Técnica {self.fake.last_name()}",
                    f"Centro de Educação Tecnológica de {city}"
                ],
                InstitutionType.DISTANCE_LEARNING: [
                    f"Universidade Virtual {self.fake.last_name()}",
                    f"Centro de EAD {city}",
                    f"Instituto Digital de Educação Superior"
                ],
                InstitutionType.POSTGRADUATE: [
                    f"Instituto de Pós-Graduação {self.fake.last_name()}",
                    f"Escola de Negócios {city}",
                    f"Centro de Estudos Avançados em {random.choice(['Gestão', 'Direito', 'Saúde'])}"
                ]
            }
            
            name = random.choice(name_patterns[inst_type])
            
            # Generate courses based on institution type
            courses = []
            if inst_type == InstitutionType.UNIVERSITY:
                num_courses = random.randint(15, 40)
                course_types = ['bachelor', 'postgraduate']
            elif inst_type == InstitutionType.COLLEGE:
                num_courses = random.randint(5, 20)
                course_types = ['bachelor', 'technologist']
            elif inst_type == InstitutionType.TECHNICAL_SCHOOL:
                num_courses = random.randint(3, 10)
                course_types = ['technologist']
            elif inst_type == InstitutionType.DISTANCE_LEARNING:
                num_courses = random.randint(10, 25)
                course_types = ['bachelor', 'technologist', 'postgraduate']
            else:  # POSTGRADUATE
                num_courses = random.randint(5, 15)
                course_types = ['postgraduate']
            
            # Build pool of available courses for this institution type
            course_pool = []
            for course_type in course_types:
                course_pool.extend([(course, course_type) for course in COURSES[course_type]])
            
            # Sample courses without replacement to avoid duplicates
            num_courses = min(num_courses, len(course_pool))
            selected_courses = random.sample(course_pool, num_courses)
            
            for course_name, course_type in selected_courses:
                duration = {
                    'bachelor': random.choice([8, 10, 12]),
                    'technologist': random.choice([4, 5, 6]),
                    'postgraduate': random.choice([2, 3, 4])
                }[course_type]
                
                # Distance learning typically cheaper
                if inst_type == InstitutionType.DISTANCE_LEARNING:
                    monthly_fee = float(random.randint(300, 1500))
                else:
                    monthly_fee = float(random.randint(800, 5000))
                
                courses.append({
                    'name': course_name,
                    'degree_type': course_type,
                    'duration_semesters': duration,
                    'monthly_fee': monthly_fee,
                    'is_active': random.random() < 0.9
                })
            
            # Get neighborhoods
            neighborhoods = NEIGHBORHOODS.get(city, ['Centro', 'Jardim', 'Vila Nova', 'Distrito Industrial'])
            
            institution = {
                '_id': ObjectId(),
                'name': name,
                'institution_type': inst_type.value,
                'cnpj': cnpj,
                'mec_code': mec_code,
                'address': {
                    'street': self.fake.street_name(),
                    'number': str(random.randint(1, 9999)),
                    'complement': random.choice(['', 'Sala 101', 'Andar 2', 'Bloco B', 'Prédio Central']),
                    'neighborhood': random.choice(neighborhoods),
                    'city': city,
                    'state': state,
                    'zip_code': self.generate_zip_code(state, city),
                    'latitude': float(self.fake.latitude()),
                    'longitude': float(self.fake.longitude())
                },
                'courses': courses,
                'total_students': random.randint(500, 20000),
                'rating': round(random.uniform(3.0, 5.0), 1) if random.random() < 0.8 else None,
                'accepts_fies': random.random() < 0.8,
                'accepts_prouni': random.random() < 0.7,
                'created_at': self.fake.date_time_between(start_date='-10y', end_date='-6m'),
                'updated_at': self.fake.date_time_between(start_date='-6m', end_date='now')
            }
            
            institutions.append(institution)
        
        # Bulk insert
        if institutions:
            logger.info(f"About to insert {len(institutions)} institutions to database...")
            self.db.institutions.insert_many(institutions)
            self.institution_ids = [inst['_id'] for inst in institutions]
            logger.info(f"Successfully inserted {len(institutions)} institutions")
    
    def seed_funding_programs(self, count: int):
        """Generate and insert funding program documents"""
        programs = []
        
        # Core government programs
        core_programs = [
            {
                'name': 'FIES - Fundo de Financiamento Estudantil',
                'program_type': FundingProgramType.FIES,
                'description': 'Programa do Governo Federal destinado a financiar a graduação na educação superior de estudantes matriculados em cursos superiores não gratuitas.',
                'max_funding_amount': float(50000.00),
                'coverage_percentage': 0.50,  # 50% coverage
                'criteria': {
                    'min_age': 18,
                    'max_income': float(20000.00),  # Family income per capita
                    'min_score': 450.0,  # ENEM score
                    'restricted_states': []
                }
            },
            {
                'name': 'ProUni - Programa Universidade para Todos',
                'program_type': FundingProgramType.PROUNI,
                'description': 'Programa do Ministério da Educação que oferece bolsas de estudo integrais e parciais em instituições privadas de educação superior.',
                'max_funding_amount': float(30000.00),
                'coverage_percentage': 1.0,  # 100% coverage for integral scholarships
                'criteria': {
                    'min_age': 17,
                    'max_income': float(4500.00),  # 3 minimum wages per capita
                    'min_score': 450.0,
                    'restricted_states': []
                }
            },
            {
                'name': 'ProUni Parcial',
                'program_type': FundingProgramType.PROUNI,
                'description': 'Bolsas parciais do ProUni para estudantes com renda familiar per capita de até três salários mínimos.',
                'max_funding_amount': float(15000.00),
                'coverage_percentage': 0.5,  # 50% coverage
                'criteria': {
                    'min_age': 17,
                    'max_income': float(6000.00),  # Higher income limit for partial
                    'min_score': 450.0,
                    'restricted_states': []
                }
            }
        ]
        
        # State and institutional programs
        state_programs = [
            {
                'name': 'Bolsa Universidade São Paulo',
                'program_type': FundingProgramType.STATE_PROGRAM,
                'state': 'SP',
                'max_funding': float(25000.00),
                'coverage': 0.7
            },
            {
                'name': 'Programa Universidade Gratuita MG',
                'program_type': FundingProgramType.STATE_PROGRAM,
                'state': 'MG',
                'max_funding': float(20000.00),
                'coverage': 0.8
            },
            {
                'name': 'Bolsa Universitária RJ',
                'program_type': FundingProgramType.STATE_PROGRAM,
                'state': 'RJ',
                'max_funding': float(22000.00),
                'coverage': 0.6
            },
            {
                'name': 'Programa Educação Superior BA',
                'program_type': FundingProgramType.STATE_PROGRAM,
                'state': 'BA',
                'max_funding': float(18000.00),
                'coverage': 0.75
            }
        ]
        
        # Add core programs
        for prog_data in core_programs:
            # Generate requirements
            requirements = []
            
            # Common requirements for all programs
            common_reqs = [
                {
                    'name': 'Comprovante de Renda',
                    'description': 'Comprovante de renda familiar de todos os membros',
                    'document_types': [DocumentType.PROOF_OF_INCOME, DocumentType.TAX_DECLARATION],
                    'is_mandatory': True
                },
                {
                    'name': 'Documentos Pessoais',
                    'description': 'RG e CPF do candidato',
                    'document_types': [DocumentType.RG, DocumentType.CPF],
                    'is_mandatory': True
                },
                {
                    'name': 'Comprovante de Residência',
                    'description': 'Comprovante de endereço atualizado',
                    'document_types': [DocumentType.PROOF_OF_ADDRESS],
                    'is_mandatory': True
                },
                {
                    'name': 'Histórico Escolar',
                    'description': 'Histórico escolar do ensino médio',
                    'document_types': [DocumentType.ACADEMIC_TRANSCRIPT],
                    'is_mandatory': True
                }
            ]
            
            if prog_data['program_type'] == FundingProgramType.FIES:
                common_reqs.append({
                    'name': 'Comprovante Bancário',
                    'description': 'Extrato bancário dos últimos 3 meses',
                    'document_types': [DocumentType.BANK_STATEMENT],
                    'is_mandatory': True
                })
            
            program = {
                '_id': ObjectId(),
                'name': prog_data['name'],
                'program_type': prog_data['program_type'],
                'description': prog_data['description'],
                'requirements': common_reqs,
                'criteria': prog_data['criteria'],
                'max_funding_amount': prog_data['max_funding_amount'],
                'coverage_percentage': prog_data['coverage_percentage'],
                'is_active': True,
                'start_date': datetime(2020, 1, 1),
                'end_date': None,
                'created_at': datetime(2020, 1, 1),
                'updated_at': datetime.utcnow()
            }
            
            programs.append(program)
        
        # Add state programs
        for state_prog in state_programs[:count - len(programs)]:
            requirements = [
                {
                    'name': 'Comprovante de Residência no Estado',
                    'description': f'Comprovante de residência no estado de {state_prog["state"]} há pelo menos 2 anos',
                    'document_types': [DocumentType.PROOF_OF_ADDRESS],
                    'is_mandatory': True
                },
                {
                    'name': 'Documentos Pessoais',
                    'description': 'RG e CPF do candidato',
                    'document_types': [DocumentType.RG, DocumentType.CPF],
                    'is_mandatory': True
                },
                {
                    'name': 'Comprovante de Renda',
                    'description': 'Comprovante de renda familiar',
                    'document_types': [DocumentType.PROOF_OF_INCOME],
                    'is_mandatory': True
                }
            ]
            
            program = {
                '_id': ObjectId(),
                'name': state_prog['name'],
                'program_type': state_prog['program_type'],
                'description': f'Programa estadual de bolsas de estudo para residentes do estado de {state_prog["state"]}',
                'requirements': requirements,
                'criteria': {
                    'min_age': 17,
                    'max_income': float(8000.00),
                    'min_score': 400.0,
                    'restricted_states': [s for s in BRAZILIAN_STATES.keys() if s != state_prog['state']]
                },
                'max_funding_amount': state_prog['max_funding'],
                'coverage_percentage': state_prog['coverage'],
                'is_active': True,
                'start_date': self.fake.date_time_between(start_date='-3y', end_date='-2y'),
                'end_date': None,
                'created_at': self.fake.date_time_between(start_date='-3y', end_date='-2y'),
                'updated_at': datetime.utcnow()
            }
            
            programs.append(program)
        
        # Add institutional programs if needed
        remaining = count - len(programs)
        for i in range(remaining):
            institution = random.choice(self.institution_ids)
            
            program = {
                '_id': ObjectId(),
                'name': f'Bolsa Mérito Acadêmico {i+1}',
                'program_type': FundingProgramType.INSTITUTIONAL,
                'description': 'Programa institucional de bolsas por mérito acadêmico',
                'requirements': [
                    {
                        'name': 'Histórico Escolar',
                        'description': 'Histórico com média acima de 8.0',
                        'document_types': [DocumentType.ACADEMIC_TRANSCRIPT],
                        'is_mandatory': True
                    },
                    {
                        'name': 'Carta de Recomendação',
                        'description': 'Carta de recomendação de professor',
                        'document_types': [DocumentType.OTHER],
                        'is_mandatory': False
                    }
                ],
                'criteria': {
                    'min_age': 17,
                    'min_score': 600.0,
                    'allowed_courses': random.sample(list(COURSES['bachelor']), k=5)
                },
                'max_funding_amount': float(random.randint(10000, 30000)),
                'coverage_percentage': random.choice([0.25, 0.5, 0.75, 1.0]),
                'is_active': random.random() < 0.9,
                'start_date': self.fake.date_time_between(start_date='-2y', end_date='-1y'),
                'end_date': None if random.random() < 0.7 else self.fake.date_time_between(start_date='+6m', end_date='+2y'),
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='-1y'),
                'updated_at': datetime.utcnow()
            }
            
            programs.append(program)
        
        # Bulk insert
        if programs:
            self.db.funding_programs.insert_many(programs)
            self.funding_program_ids = [prog['_id'] for prog in programs]
            logger.info(f"Inserted {len(programs)} funding programs")
    
    def seed_workflows(self, count: int):
        """Generate and insert workflow documents"""
        workflows = []
        
        # Standard workflow steps
        standard_steps = [
            {
                'stage': WorkflowStage.APPLICATION_RECEIVED,
                'assigned_role': UserRole.STAFF,
                'sla_hours': 24,
                'auto_approve': False,
                'approval_criteria': {}
            },
            {
                'stage': WorkflowStage.DOCUMENT_VERIFICATION,
                'assigned_role': UserRole.REVIEWER,
                'sla_hours': 48,
                'auto_approve': False,
                'approval_criteria': {'all_documents_verified': True}
            },
            {
                'stage': WorkflowStage.ACADEMIC_REVIEW,
                'assigned_role': UserRole.REVIEWER,
                'sla_hours': 72,
                'auto_approve': False,
                'approval_criteria': {'min_score': 450}
            },
            {
                'stage': WorkflowStage.FINANCIAL_REVIEW,
                'assigned_role': UserRole.REVIEWER,
                'sla_hours': 48,
                'auto_approve': False,
                'approval_criteria': {'income_verified': True}
            },
            {
                'stage': WorkflowStage.FINAL_APPROVAL,
                'assigned_role': UserRole.ADMIN,
                'sla_hours': 24,
                'auto_approve': False,
                'approval_criteria': {}
            },
            {
                'stage': WorkflowStage.ENROLLMENT,
                'assigned_role': UserRole.STAFF,
                'sla_hours': 48,
                'auto_approve': True,
                'approval_criteria': {'payment_confirmed': True}
            }
        ]
        
        # Create workflows for each funding program
        for i, program_id in enumerate(self.funding_program_ids[:count]):
            # Get program details
            program = self.db.funding_programs.find_one({'_id': program_id})
            
            # Customize workflow based on program type
            steps = standard_steps.copy()
            
            if program['program_type'] == FundingProgramType.FIES:
                # FIES has more stringent financial review
                steps[3]['sla_hours'] = 96  # Longer financial review
                steps[3]['approval_criteria']['credit_check'] = True
            elif program['program_type'] == FundingProgramType.PROUNI:
                # ProUni focuses on academic merit
                steps[2]['sla_hours'] = 96  # Longer academic review
                steps[2]['approval_criteria']['min_score'] = 450
            elif program['program_type'] == FundingProgramType.INSTITUTIONAL:
                # Institutional programs may have simplified workflows
                steps = steps[:4] + steps[5:]  # Skip final approval
            
            workflow = {
                '_id': ObjectId(),
                'name': f'Workflow - {program["name"]}',
                'funding_program_id': program_id,
                'steps': steps,
                'is_active': True,
                'created_at': program['created_at'],
                'updated_at': datetime.utcnow()
            }
            
            workflows.append(workflow)
        
        # Add some inactive/archived workflows
        remaining = count - len(workflows)
        for i in range(remaining):
            program_id = random.choice(self.funding_program_ids)
            
            workflow = {
                '_id': ObjectId(),
                'name': f'Workflow Arquivado {i+1}',
                'funding_program_id': program_id,
                'steps': random.sample(standard_steps, k=random.randint(3, 5)),
                'is_active': False,
                'created_at': self.fake.date_time_between(start_date='-3y', end_date='-1y'),
                'updated_at': self.fake.date_time_between(start_date='-1y', end_date='-6m')
            }
            
            workflows.append(workflow)
        
        # Bulk insert
        if workflows:
            # Convert all enum values to their string representations
            workflows = [self._convert_enums_to_values(workflow) for workflow in workflows]
            self.db.workflows.insert_many(workflows)
            self.workflow_ids = [wf['_id'] for wf in workflows]
            logger.info(f"Inserted {len(workflows)} workflows")
    
    def seed_users(self, count: int):
        """Generate and insert user documents"""
        users = []
        used_emails = set()
        used_cpfs = set()
        
        # Distribution of user roles
        role_distribution = [
            (UserRole.APPLICANT, 0.6),    # 60% applicants
            (UserRole.STUDENT, 0.2),       # 20% students
            (UserRole.STAFF, 0.1),         # 10% staff
            (UserRole.REVIEWER, 0.07),     # 7% reviewers
            (UserRole.ADMIN, 0.02),        # 2% admins
            (UserRole.INSTITUTION_ADMIN, 0.01)  # 1% institution admins
        ]
        
        for i in range(count):
            # Generate unique CPF
            cpf = self.generate_cpf()
            while cpf in used_cpfs:
                cpf = self.generate_cpf()
            used_cpfs.add(cpf)
            
            # Generate unique email
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            email_base = f"{first_name.lower()}.{last_name.lower()}"
            email_domain = random.choice(['gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com', 'uol.com.br'])
            email = f"{email_base}@{email_domain}"
            
            # Ensure uniqueness
            counter = 1
            while email in used_emails:
                email = f"{email_base}{counter}@{email_domain}"
                counter += 1
            used_emails.add(email)
            
            # Choose role based on distribution
            role = random.choices(
                [r[0] for r in role_distribution],
                weights=[r[1] for r in role_distribution]
            )[0]
            
            # Generate permissions based on role
            permissions = []
            if role == UserRole.ADMIN:
                permissions = [
                    {'resource': 'applications', 'actions': ['create', 'read', 'update', 'delete']},
                    {'resource': 'users', 'actions': ['create', 'read', 'update', 'delete']},
                    {'resource': 'institutions', 'actions': ['create', 'read', 'update', 'delete']},
                    {'resource': 'reports', 'actions': ['create', 'read']}
                ]
            elif role == UserRole.INSTITUTION_ADMIN:
                institution_id = random.choice(self.institution_ids)
                permissions = [
                    {'resource': 'applications', 'actions': ['read', 'update'], 'institution_id': institution_id},
                    {'resource': 'students', 'actions': ['read'], 'institution_id': institution_id},
                    {'resource': 'reports', 'actions': ['read'], 'institution_id': institution_id}
                ]
            elif role == UserRole.REVIEWER:
                permissions = [
                    {'resource': 'applications', 'actions': ['read', 'update']},
                    {'resource': 'documents', 'actions': ['read', 'update']}
                ]
            elif role == UserRole.STAFF:
                permissions = [
                    {'resource': 'applications', 'actions': ['read', 'update']},
                    {'resource': 'students', 'actions': ['read', 'create']}
                ]
            
            # Institution associations
            institution_ids = []
            if role in [UserRole.INSTITUTION_ADMIN, UserRole.STAFF]:
                # Assign to 1-3 institutions
                num_institutions = random.randint(1, min(3, len(self.institution_ids)))
                institution_ids = random.sample(self.institution_ids, num_institutions)
            
            # Password hash (simulated)
            password_hash = hashlib.sha256(f"senha{i:06d}".encode()).hexdigest()
            
            # Activity patterns
            created_date = self.fake.date_time_between(start_date='-3y', end_date='-1d')
            last_login = None
            if random.random() < 0.8:  # 80% have logged in
                last_login = self.fake.date_time_between(start_date=created_date, end_date='now')
            
            user = {
                '_id': ObjectId(),
                'email': email,
                'cpf': cpf,
                'password_hash': password_hash,
                'full_name': f"{first_name} {last_name}",
                'phone': self.generate_brazilian_phone(),
                'role': role,
                'permissions': permissions,
                'institution_ids': institution_ids,
                'is_active': random.random() < 0.95,  # 95% active
                'last_login': last_login,
                'created_at': created_date,
                'updated_at': self.fake.date_time_between(start_date=created_date, end_date='now')
            }
            
            users.append(user)
            self.cpf_to_user[cpf] = user['_id']
            
            # Log progress
            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1}/{count} users...")
        
        # Bulk insert in batches
        batch_size = 1000
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            # Convert all enum values to their string representations
            batch = [self._convert_enums_to_values(user) for user in batch]
            self.db.users.insert_many(batch)
            
        self.user_ids = [user['_id'] for user in users]
        logger.info(f"Inserted {len(users)} users")
    
    def seed_students(self, count: int):
        """Generate and insert student documents"""
        students = []
        used_cpfs = set()
        
        # Get users with student or applicant role
        student_users = list(self.db.users.find({'role': {'$in': [UserRole.STUDENT, UserRole.APPLICANT]}}).limit(count))
        
        for i, user in enumerate(student_users):
            # Reuse CPF from user
            cpf = user['cpf']
            if cpf in used_cpfs:
                continue
            used_cpfs.add(cpf)
            
            # Generate address
            state = random.choice(list(BRAZILIAN_STATES.keys()))
            city = random.choice(BRAZILIAN_STATES[state]['cities'])
            neighborhoods = NEIGHBORHOODS.get(city, ['Centro', 'Jardim', 'Vila'])
            
            address = {
                'street': self.fake.street_name(),
                'number': str(random.randint(1, 9999)),
                'complement': random.choice(['', 'Apto 101', 'Casa 2', 'Bloco A', 'Fundos']),
                'neighborhood': random.choice(neighborhoods),
                'city': city,
                'state': state,
                'zip_code': self.generate_zip_code(state, city)
            }
            
            # Generate enrollments
            enrollments = []
            if user['role'] == UserRole.STUDENT:
                # Active students have enrollments
                num_enrollments = random.randint(1, 3)
                
                for j in range(num_enrollments):
                    institution_id = random.choice(self.institution_ids)
                    institution = self.db.institutions.find_one({'_id': institution_id})
                    
                    if institution and institution['courses']:
                        course = random.choice(institution['courses'])
                        
                        # Calculate semester
                        enrollment_date = self.fake.date_time_between(start_date='-4y', end_date='-6m')
                        semesters_passed = (datetime.utcnow() - enrollment_date).days // 180
                        current_semester = f"2024.{1 if datetime.utcnow().month <= 6 else 2}"
                        
                        status = random.choices(
                            ['active', 'completed', 'dropped', 'transferred'],
                            weights=[0.7, 0.15, 0.1, 0.05]
                        )[0]
                        
                        completion_date = None
                        if status == 'completed':
                            completion_date = enrollment_date + timedelta(days=course['duration_semesters'] * 180)
                        elif status in ['dropped', 'transferred']:
                            completion_date = self.fake.date_time_between(
                                start_date=enrollment_date,
                                end_date=min(datetime.utcnow(), enrollment_date + timedelta(days=365))
                            )
                        
                        enrollments.append({
                            'institution_id': institution_id,
                            'course_name': course['name'],
                            'semester': current_semester,
                            'enrollment_date': enrollment_date,
                            'status': status,
                            'completion_date': completion_date
                        })
            
            # Calculate total funding and engagement
            total_funding = float(0.00)
            if enrollments:
                # Students with enrollments may have received funding
                total_funding = float(random.randint(0, 50000))
            
            # Engagement score based on activity
            engagement_score = random.uniform(0.0, 10.0)
            if user['last_login'] and (datetime.utcnow() - user['last_login']).days < 30:
                engagement_score = min(10.0, engagement_score + 2.0)
            
            # Birth date (18-45 years old)
            age = random.randint(18, 45)
            birth_date = datetime.utcnow() - timedelta(days=age * 365 + random.randint(0, 365))
            
            student = {
                '_id': ObjectId(),
                'user_id': user['_id'],
                'cpf': cpf,
                'full_name': user['full_name'],
                'birth_date': birth_date,
                'gender': random.choice(['M', 'F', 'Other']),
                'address': address,
                'enrollments': enrollments,
                'total_funding_received': total_funding,
                'engagement_score': round(engagement_score, 2),
                'created_at': user['created_at'],
                'updated_at': datetime.utcnow()
            }
            
            students.append(student)
            self.user_to_student[user['_id']] = student['_id']
            
            # Log progress
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i + 1}/{count} students...")
        
        # Bulk insert in batches
        batch_size = 1000
        for i in range(0, len(students), batch_size):
            batch = students[i:i + batch_size]
            self.db.students.insert_many(batch)
        
        self.student_ids = [student['_id'] for student in students]
        logger.info(f"Inserted {len(students)} students")
    
    def seed_applications(self, count: int):
        """Generate and insert application documents (57,000 per semester)"""
        applications = []
        used_protocols = set()
        
        # Define semesters
        semesters = ['2024.1', '2024.2', '2023.2', '2023.1']
        semester_weights = [0.4, 0.35, 0.15, 0.1]  # More recent semesters have more applications
        
        # Get eligible users (applicants and students)
        eligible_users = list(self.db.users.find({'role': {'$in': [UserRole.APPLICANT, UserRole.STUDENT]}}))
        
        # Status distribution
        status_weights = {
            ApplicationStatus.APPROVED: 0.25,
            ApplicationStatus.ENROLLED: 0.20,
            ApplicationStatus.UNDER_REVIEW: 0.15,
            ApplicationStatus.DOCUMENTS_PENDING: 0.10,
            ApplicationStatus.SUBMITTED: 0.10,
            ApplicationStatus.REJECTED: 0.15,
            ApplicationStatus.DRAFT: 0.03,
            ApplicationStatus.CANCELLED: 0.02
        }
        
        for i in range(count):
            # Select user
            user = random.choice(eligible_users)
            
            # Get or create student record
            student_id = self.user_to_student.get(user['_id'])
            if not student_id:
                # Create a basic student record if needed
                student_id = ObjectId()
                self.user_to_student[user['_id']] = student_id
            
            # Select semester
            semester = random.choices(semesters, weights=semester_weights)[0]
            year = int(semester.split('.')[0])
            sem_num = int(semester.split('.')[1])
            
            # Generate protocol number
            protocol_date = datetime(year, 1 if sem_num == 1 else 7, random.randint(1, 28))
            protocol = self.generate_protocol_number(year, protocol_date.month)
            while protocol in used_protocols:
                protocol = self.generate_protocol_number(year, protocol_date.month)
            used_protocols.add(protocol)
            
            # Select funding program
            funding_program_id = random.choice(self.funding_program_ids)
            funding_program = self.db.funding_programs.find_one({'_id': funding_program_id})
            
            # Select institution
            institution_id = random.choice(self.institution_ids)
            institution = self.db.institutions.find_one({'_id': institution_id})
            
            # Select course from institution
            course_name = ''
            if institution and institution['courses']:
                # Filter courses based on funding program criteria
                eligible_courses = institution['courses']
                if funding_program and 'allowed_courses' in funding_program['criteria'] and funding_program['criteria']['allowed_courses']:
                    eligible_courses = [c for c in institution['courses'] 
                                      if c['name'] in funding_program['criteria']['allowed_courses']]
                
                if eligible_courses:
                    course = random.choice(eligible_courses)
                    course_name = course['name']
                    
                    # Calculate requested amount based on course fee and coverage
                    monthly_fee = float(course['monthly_fee'])
                    duration = course['duration_semesters'] * 6  # months
                    total_cost = monthly_fee * duration
                    coverage = funding_program['coverage_percentage'] if funding_program else 0.5
                    requested_amount = float(min(total_cost * coverage, float(funding_program['max_funding_amount'])))
                else:
                    requested_amount = float(random.randint(5000, 30000))
            else:
                requested_amount = float(random.randint(5000, 30000))
            
            # Determine status
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values())
            )[0]
            
            # Calculate dates based on status
            submission_date = protocol_date + timedelta(days=random.randint(0, 30))
            decision_date = None
            approved_amount = None
            rejection_reason = None
            
            if status in [ApplicationStatus.APPROVED, ApplicationStatus.ENROLLED, ApplicationStatus.REJECTED]:
                decision_date = submission_date + timedelta(days=random.randint(15, 60))
                
                if status == ApplicationStatus.REJECTED:
                    rejection_reasons = [
                        'Renda familiar excede o limite permitido',
                        'Documentação incompleta',
                        'Não atingiu a pontuação mínima no ENEM',
                        'Curso não elegível para o programa',
                        'Já possui graduação',
                        'Irregularidade na documentação'
                    ]
                    rejection_reason = random.choice(rejection_reasons)
                else:
                    # Approved - calculate approved amount
                    approved_amount = requested_amount * random.uniform(0.7, 1.0)
            
            # Generate stage history
            stage_history = []
            current_stage = None
            
            if status != ApplicationStatus.DRAFT:
                # Application received
                stage_history.append({
                    'stage': WorkflowStage.APPLICATION_RECEIVED,
                    'status': 'completed',
                    'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                    'started_at': submission_date,
                    'completed_at': submission_date + timedelta(hours=random.randint(1, 24)),
                    'comments': 'Aplicação recebida com sucesso'
                })
                
                if status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.CANCELLED]:
                    # Document verification
                    doc_start = stage_history[-1]['completed_at']
                    stage_history.append({
                        'stage': WorkflowStage.DOCUMENT_VERIFICATION,
                        'status': 'completed' if status != ApplicationStatus.DOCUMENTS_PENDING else 'pending',
                        'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                        'started_at': doc_start,
                        'completed_at': doc_start + timedelta(days=random.randint(1, 5)) if status != ApplicationStatus.DOCUMENTS_PENDING else None,
                        'comments': 'Documentos verificados' if status != ApplicationStatus.DOCUMENTS_PENDING else 'Aguardando documentos'
                    })
                    
                    if status not in [ApplicationStatus.DOCUMENTS_PENDING, ApplicationStatus.UNDER_REVIEW]:
                        # Academic review
                        acad_start = stage_history[-1]['completed_at']
                        stage_history.append({
                            'stage': WorkflowStage.ACADEMIC_REVIEW,
                            'status': 'completed',
                            'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                            'started_at': acad_start,
                            'completed_at': acad_start + timedelta(days=random.randint(2, 7)),
                            'comments': 'Análise acadêmica concluída'
                        })
                        
                        # Financial review
                        fin_start = stage_history[-1]['completed_at']
                        stage_history.append({
                            'stage': WorkflowStage.FINANCIAL_REVIEW,
                            'status': 'completed',
                            'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                            'started_at': fin_start,
                            'completed_at': fin_start + timedelta(days=random.randint(1, 4)),
                            'comments': 'Análise financeira concluída'
                        })
                        
                        if status in [ApplicationStatus.APPROVED, ApplicationStatus.ENROLLED, ApplicationStatus.REJECTED]:
                            # Final approval
                            final_start = stage_history[-1]['completed_at']
                            stage_history.append({
                                'stage': WorkflowStage.FINAL_APPROVAL,
                                'status': 'completed',
                                'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                                'started_at': final_start,
                                'completed_at': decision_date,
                                'comments': 'Aprovado' if status != ApplicationStatus.REJECTED else f'Rejeitado: {rejection_reason}'
                            })
                            
                            if status == ApplicationStatus.ENROLLED:
                                # Enrollment
                                enroll_start = decision_date
                                stage_history.append({
                                    'stage': WorkflowStage.ENROLLMENT,
                                    'status': 'completed',
                                    'assigned_to': random.choice([uid for uid in self.user_ids if uid != user['_id']]),
                                    'started_at': enroll_start,
                                    'completed_at': enroll_start + timedelta(days=random.randint(1, 7)),
                                    'comments': 'Matrícula realizada com sucesso'
                                })
            
            # Set current stage
            if stage_history:
                incomplete_stages = [sh for sh in stage_history if sh['status'] == 'pending']
                if incomplete_stages:
                    current_stage = incomplete_stages[0]['stage']
                elif status == ApplicationStatus.UNDER_REVIEW:
                    current_stage = WorkflowStage.ACADEMIC_REVIEW
            
            # Create application
            application = {
                '_id': ObjectId(),
                'applicant_id': student_id,
                'applicant_info': {
                    'full_name': user['full_name'],
                    'cpf': user['cpf'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'birth_date': datetime.combine(self.fake.date_of_birth(minimum_age=18, maximum_age=45), datetime.min.time())
                },
                'protocol_number': protocol,
                'funding_program_id': funding_program_id,
                'institution_id': institution_id,
                'course_name': course_name,
                'semester': semester,
                'requested_amount': requested_amount,
                'approved_amount': approved_amount,
                'status': status.value,
                'stage_history': stage_history,
                'current_stage': current_stage,
                'document_ids': [],  # Will be populated when seeding documents
                'submission_date': submission_date,
                'decision_date': decision_date,
                'rejection_reason': rejection_reason,
                'version': 1,
                'created_at': protocol_date,
                'updated_at': submission_date if status != ApplicationStatus.DRAFT else protocol_date
            }
            
            applications.append(application)
            
            # Log progress
            if (i + 1) % 5000 == 0:
                logger.info(f"Generated {i + 1}/{count} applications...")
        
        # Bulk insert in batches
        batch_size = 1000
        for i in range(0, len(applications), batch_size):
            batch = applications[i:i + batch_size]
            # Convert all enum values to their string representations
            batch = [self._convert_enums_to_values(app) for app in batch]
            self.db.applications.insert_many(batch)
        
        self.application_ids = [app['_id'] for app in applications]
        logger.info(f"Inserted {len(applications)} applications")
    
    def seed_documents(self, count: int):
        """Generate and insert document records (22 per application average)"""
        documents = []
        
        # Get all applications
        applications = list(self.db.applications.find())
        
        # Document type distribution per application
        required_docs = [
            DocumentType.CPF,
            DocumentType.RG,
            DocumentType.PROOF_OF_INCOME,
            DocumentType.PROOF_OF_ADDRESS,
            DocumentType.ACADEMIC_TRANSCRIPT
        ]
        
        optional_docs = [
            DocumentType.BANK_STATEMENT,
            DocumentType.TAX_DECLARATION,
            DocumentType.PHOTO,
            DocumentType.EMPLOYMENT_CERTIFICATE,
            DocumentType.ENROLLMENT_CERTIFICATE,
            DocumentType.OTHER
        ]
        
        # Calculate documents per application
        avg_docs_per_app = count // len(applications) if applications else 22
        
        for app in applications:
            # Number of documents for this application (vary around average)
            num_docs = max(5, int(random.gauss(avg_docs_per_app, 3)))
            
            # Always include required documents
            app_doc_types = required_docs.copy()
            
            # Add some optional documents
            num_optional = num_docs - len(required_docs)
            if num_optional > 0:
                # Some documents might be submitted multiple times (updates)
                optional_choices = []
                for _ in range(num_optional):
                    doc_type = random.choice(optional_docs)
                    optional_choices.append(doc_type)
                app_doc_types.extend(optional_choices)
            
            # Generate documents
            app_documents = []
            for doc_type in app_doc_types:
                # Generate file metadata
                file_extensions = {
                    DocumentType.CPF: ['pdf', 'jpg', 'png'],
                    DocumentType.RG: ['pdf', 'jpg', 'png'],
                    DocumentType.PROOF_OF_INCOME: ['pdf'],
                    DocumentType.PROOF_OF_ADDRESS: ['pdf', 'jpg'],
                    DocumentType.ACADEMIC_TRANSCRIPT: ['pdf'],
                    DocumentType.BANK_STATEMENT: ['pdf'],
                    DocumentType.TAX_DECLARATION: ['pdf'],
                    DocumentType.PHOTO: ['jpg', 'png'],
                    DocumentType.EMPLOYMENT_CERTIFICATE: ['pdf'],
                    DocumentType.ENROLLMENT_CERTIFICATE: ['pdf'],
                    DocumentType.OTHER: ['pdf', 'jpg', 'png', 'doc', 'docx']
                }
                
                extension = random.choice(file_extensions.get(doc_type, ['pdf']))
                file_size = random.randint(100 * 1024, 5 * 1024 * 1024)  # 100KB to 5MB
                
                # File naming patterns
                file_names = {
                    DocumentType.CPF: f"cpf_{app['applicant_info']['cpf'][:6]}",
                    DocumentType.RG: f"rg_{random.randint(1000000, 9999999)}",
                    DocumentType.PROOF_OF_INCOME: f"comprovante_renda_{random.randint(1, 12):02d}_2024",
                    DocumentType.PROOF_OF_ADDRESS: f"comprovante_endereco_{random.randint(1, 12):02d}_2024",
                    DocumentType.ACADEMIC_TRANSCRIPT: "historico_escolar",
                    DocumentType.BANK_STATEMENT: f"extrato_bancario_{random.randint(1, 12):02d}_2024",
                    DocumentType.TAX_DECLARATION: "declaracao_irpf_2024",
                    DocumentType.PHOTO: "foto_3x4",
                    DocumentType.EMPLOYMENT_CERTIFICATE: "declaracao_emprego",
                    DocumentType.ENROLLMENT_CERTIFICATE: "comprovante_matricula",
                    DocumentType.OTHER: f"documento_{random.randint(1, 999):03d}"
                }
                
                file_name = f"{file_names.get(doc_type, 'documento')}.{extension}"
                
                # Upload date based on application status
                upload_date = app['submission_date']
                if app['status'] == ApplicationStatus.DRAFT:
                    upload_date = app['created_at']
                elif app['status'] == ApplicationStatus.DOCUMENTS_PENDING:
                    # Some documents uploaded, waiting for others
                    if random.random() < 0.6:
                        upload_date = app['submission_date'] + timedelta(days=random.randint(1, 10))
                    else:
                        continue  # Skip this document (not uploaded yet)
                
                # Verification status based on application status
                verification_history = []
                current_status = 'pending'
                
                if app['status'] in [ApplicationStatus.APPROVED, ApplicationStatus.ENROLLED, ApplicationStatus.REJECTED]:
                    # Documents were verified
                    reviewer_id = random.choice([uid for uid in self.user_ids if uid != app['applicant_id']])
                    verification_date = upload_date + timedelta(days=random.randint(1, 5))
                    
                    if app['status'] == ApplicationStatus.REJECTED and random.random() < 0.3:
                        # Some documents might be rejected
                        current_status = 'rejected'
                        rejection_reasons = [
                            'Documento ilegível',
                            'Documento vencido',
                            'Documento incompleto',
                            'Documento não corresponde ao solicitado'
                        ]
                        verification_history.append({
                            'reviewer_id': reviewer_id,
                            'status': 'rejected',
                            'verified_at': verification_date,
                            'comments': random.choice(rejection_reasons),
                            'rejection_reason': random.choice(rejection_reasons)
                        })
                    else:
                        current_status = 'verified'
                        verification_history.append({
                            'reviewer_id': reviewer_id,
                            'status': 'approved',
                            'verified_at': verification_date,
                            'comments': 'Documento verificado e aprovado'
                        })
                
                # Check if document should be archived
                is_archived = False
                archive_date = None
                if app['decision_date'] and (datetime.utcnow() - app['decision_date']).days > 365:
                    # Archive documents older than 1 year after decision
                    if random.random() < 0.1:  # 10% chance of archival
                        is_archived = True
                        archive_date = app['decision_date'] + timedelta(days=365 + random.randint(0, 180))
                
                # Generate checksum
                checksum = hashlib.md5(f"{file_name}{file_size}{upload_date}".encode()).hexdigest()
                
                document = {
                    '_id': ObjectId(),
                    'application_id': app['_id'],
                    'applicant_id': app['applicant_id'],
                    'document_type': doc_type,
                    'metadata': {
                        'file_name': file_name,
                        'file_size': file_size,
                        'mime_type': f"{'image' if extension in ['jpg', 'png'] else 'application'}/{extension}",
                        'upload_date': upload_date,
                        'storage_path': f"/documents/{app['semester']}/{app['applicant_id']}/{ObjectId()}/{file_name}",
                        'checksum': checksum
                    },
                    'verification_history': verification_history,
                    'current_status': current_status,
                    'is_archived': is_archived,
                    'archive_date': archive_date,
                    'version': len([d for d in app_documents if d['document_type'] == doc_type]) + 1,
                    'created_at': upload_date,
                    'updated_at': verification_history[-1]['verified_at'] if verification_history else upload_date
                }
                
                app_documents.append(document)
            
            # Update application with document IDs
            doc_ids = [doc['_id'] for doc in app_documents]
            self.db.applications.update_one(
                {'_id': app['_id']},
                {'$set': {'document_ids': doc_ids}}
            )
            
            documents.extend(app_documents)
            
            # Log progress
            if len(documents) % 10000 == 0:
                logger.info(f"Generated {len(documents)} documents...")
            
            # Insert in batches to avoid memory issues
            if len(documents) >= 10000:
                # Convert all enum values to their string representations
                documents = [self._convert_enums_to_values(doc) for doc in documents]
                self.db.documents.insert_many(documents)
                documents = []
        
        # Insert remaining documents
        if documents:
            # Convert all enum values to their string representations
            documents = [self._convert_enums_to_values(doc) for doc in documents]
            self.db.documents.insert_many(documents)
        
        logger.info(f"Inserted documents for all applications")
    
    def seed_protocols(self):
        """Generate protocol records for all applications"""
        protocols = []
        
        # Get all applications that don't have protocols yet
        applications = list(self.db.applications.find())
        
        for app in applications:
            # Generate QR code data
            qr_data = f"EDTECH-BR:{app['protocol_number']}:{app['_id']}"
            qr_code = hashlib.sha256(qr_data.encode()).hexdigest()[:32]
            
            # Generate access code (6 digits)
            access_code = f"{random.randint(100000, 999999)}"
            
            protocol = {
                '_id': ObjectId(),
                'protocol_number': app['protocol_number'],
                'application_id': app['_id'],
                'created_at': app['created_at'],
                'qr_code': qr_code,
                'access_code': access_code
            }
            
            protocols.append(protocol)
            
            # Insert in batches
            if len(protocols) >= 1000:
                # Convert all enum values to their string representations
                protocols = [self._convert_enums_to_values(protocol) for protocol in protocols]
                self.db.protocols.insert_many(protocols)
                protocols = []
        
        # Insert remaining
        if protocols:
            # Convert all enum values to their string representations
            protocols = [self._convert_enums_to_values(protocol) for protocol in protocols]
            self.db.protocols.insert_many(protocols)
        
        logger.info(f"Created protocols for all applications")
    
    def seed_notifications(self, count: int):
        """Generate and insert notification documents"""
        notifications = []
        
        # Get sample of applications and users
        applications = list(self.db.applications.find().limit(count // 10))
        users = list(self.db.users.find())
        
        # Notification templates
        templates = {
            'application_received': {
                'subject': 'Aplicação Recebida - Protocolo {protocol}',
                'content': 'Sua aplicação foi recebida com sucesso. Protocolo: {protocol}. Acompanhe o status em nosso portal.',
                'type': 'email'
            },
            'documents_pending': {
                'subject': 'Documentos Pendentes - Protocolo {protocol}',
                'content': 'Existem documentos pendentes em sua aplicação {protocol}. Por favor, acesse o portal para enviar os documentos faltantes.',
                'type': 'email'
            },
            'application_approved': {
                'subject': 'Aplicação Aprovada! - Protocolo {protocol}',
                'content': 'Parabéns! Sua aplicação {protocol} foi aprovada. Valor aprovado: R$ {amount}. Próximos passos no portal.',
                'type': 'email'
            },
            'application_rejected': {
                'subject': 'Aplicação Não Aprovada - Protocolo {protocol}',
                'content': 'Infelizmente sua aplicação {protocol} não foi aprovada. Motivo: {reason}. Você pode aplicar novamente no próximo semestre.',
                'type': 'email'
            },
            'document_verified': {
                'subject': 'Documento Verificado',
                'content': 'O documento {doc_type} foi verificado com sucesso.',
                'type': 'in_app'
            },
            'reminder_incomplete': {
                'subject': 'Lembrete: Complete sua Aplicação',
                'content': 'Sua aplicação {protocol} está incompleta. Complete o processo para participar do programa de financiamento.',
                'type': 'sms'
            },
            'system_maintenance': {
                'subject': 'Manutenção Programada do Sistema',
                'content': 'O sistema estará em manutenção no dia {date} das {start} às {end}.',
                'type': 'email'
            }
        }
        
        for i in range(count):
            # Choose notification scenario
            scenario = random.choice(list(templates.keys()))
            template = templates[scenario]
            
            # Select recipient
            if scenario == 'system_maintenance':
                # Broadcast to multiple users
                recipient = random.choice(users)
            else:
                # Application-related notification
                app = random.choice(applications)
                recipient = next((u for u in users if u['cpf'] == app['applicant_info']['cpf']), None)
                if not recipient:
                    continue
            
            # Generate notification details
            subject = template['subject']
            content = template['content']
            
            # Replace placeholders
            if 'application' in locals():
                subject = subject.replace('{protocol}', app['protocol_number'])
                content = content.replace('{protocol}', app['protocol_number'])
                
                if '{amount}' in content and app.get('approved_amount'):
                    content = content.replace('{amount}', f"{app['approved_amount']:,.2f}")
                
                if '{reason}' in content and app.get('rejection_reason'):
                    content = content.replace('{reason}', app['rejection_reason'])
            
            if '{date}' in content:
                date = self.fake.date_between(start_date='+1d', end_date='+30d')
                content = content.replace('{date}', date.strftime('%d/%m/%Y'))
                content = content.replace('{start}', '22:00')
                content = content.replace('{end}', '02:00')
            
            if '{doc_type}' in content:
                content = content.replace('{doc_type}', random.choice(['CPF', 'Comprovante de Renda', 'Histórico Escolar']))
            
            # Determine status
            created_date = self.fake.date_time_between(start_date='-6m', end_date='now')
            status = random.choices(
                ['sent', 'delivered', 'failed', 'pending'],
                weights=[0.4, 0.5, 0.05, 0.05]
            )[0]
            
            sent_at = None
            delivered_at = None
            error_message = None
            
            if status in ['sent', 'delivered', 'failed']:
                sent_at = created_date + timedelta(seconds=random.randint(1, 300))
                
                if status == 'delivered':
                    delivered_at = sent_at + timedelta(seconds=random.randint(1, 60))
                elif status == 'failed':
                    error_messages = [
                        'Invalid email address',
                        'Mailbox full',
                        'SMS delivery failed',
                        'User opted out'
                    ]
                    error_message = random.choice(error_messages)
            
            # Determine related entity
            related_entity_type = 'application' if 'app' in locals() else 'workflow'
            related_entity_id = app['_id'] if 'app' in locals() else random.choice(self.workflow_ids)
            
            notification = {
                '_id': ObjectId(),
                'recipient_id': recipient['_id'],
                'recipient_email': recipient['email'],
                'notification_type': template['type'],
                'subject': subject,
                'content': content,
                'related_entity_type': related_entity_type,
                'related_entity_id': related_entity_id,
                'status': status,
                'sent_at': sent_at,
                'delivered_at': delivered_at,
                'error_message': error_message,
                'created_at': created_date
            }
            
            notifications.append(notification)
            
            # Insert in batches
            if len(notifications) >= 1000:
                # Convert all enum values to their string representations
                notifications = [self._convert_enums_to_values(notif) for notif in notifications]
                self.db.notifications.insert_many(notifications)
                notifications = []
                
        # Insert remaining
        if notifications:
            # Convert all enum values to their string representations
            notifications = [self._convert_enums_to_values(notif) for notif in notifications]
            self.db.notifications.insert_many(notifications)
        
        logger.info(f"Inserted {count} notifications")
    
    def seed_audit_logs(self, count: int):
        """Generate and insert audit log documents"""
        audit_logs = []
        
        # Get samples of various entities
        users = list(self.db.users.find().limit(1000))
        applications = list(self.db.applications.find().limit(1000))
        documents = list(self.db.documents.find().limit(1000))
        
        # Action templates
        actions = [
            {
                'action': 'user.login',
                'entity_type': 'user',
                'changes': lambda: {'last_login': datetime.utcnow().isoformat()}
            },
            {
                'action': 'application.create',
                'entity_type': 'application',
                'changes': lambda: {'status': 'draft', 'created': True}
            },
            {
                'action': 'application.submit',
                'entity_type': 'application',
                'changes': lambda: {'status': {'from': 'draft', 'to': 'submitted'}}
            },
            {
                'action': 'application.update_status',
                'entity_type': 'application',
                'changes': lambda: {
                    'status': {
                        'from': random.choice(['submitted', 'under_review']),
                        'to': random.choice(['approved', 'rejected', 'documents_pending'])
                    }
                }
            },
            {
                'action': 'document.upload',
                'entity_type': 'document',
                'changes': lambda: {'file_name': f"document_{random.randint(1, 999)}.pdf", 'uploaded': True}
            },
            {
                'action': 'document.verify',
                'entity_type': 'document',
                'changes': lambda: {
                    'status': {'from': 'pending', 'to': random.choice(['verified', 'rejected'])},
                    'verified_by': str(random.choice(users)['_id'])
                }
            },
            {
                'action': 'user.update_profile',
                'entity_type': 'user',
                'changes': lambda: {
                    'fields_updated': random.sample(['phone', 'email', 'address'], k=random.randint(1, 2))
                }
            },
            {
                'action': 'application.assign_reviewer',
                'entity_type': 'application',
                'changes': lambda: {
                    'assigned_to': str(random.choice(users)['_id']),
                    'stage': random.choice(['document_verification', 'academic_review', 'financial_review'])
                }
            }
        ]
        
        # IP addresses (Brazilian ISPs)
        ip_ranges = [
            '177.', '179.', '187.', '189.', '191.', '201.'  # Common Brazilian IP prefixes
        ]
        
        # User agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0'
        ]
        
        for i in range(count):
            # Select action
            action_template = random.choice(actions)
            
            # Select user performing the action
            user = random.choice(users)
            
            # Select entity based on action
            if action_template['entity_type'] == 'user':
                entity_id = random.choice(users)['_id']
            elif action_template['entity_type'] == 'application':
                entity_id = random.choice(applications)['_id'] if applications else ObjectId()
            elif action_template['entity_type'] == 'document':
                entity_id = random.choice(documents)['_id'] if documents else ObjectId()
            else:
                entity_id = ObjectId()
            
            # Generate IP address
            ip_prefix = random.choice(ip_ranges)
            ip_address = f"{ip_prefix}{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            # Generate timestamp (distributed over last 6 months)
            timestamp = self.fake.date_time_between(start_date='-6m', end_date='now')
            
            audit_log = {
                '_id': ObjectId(),
                'user_id': user['_id'],
                'action': action_template['action'],
                'entity_type': action_template['entity_type'],
                'entity_id': entity_id,
                'changes': action_template['changes'](),
                'ip_address': ip_address,
                'user_agent': random.choice(user_agents),
                'timestamp': timestamp
            }
            
            audit_logs.append(audit_log)
            
            # Insert in batches
            if len(audit_logs) >= 1000:
                # Convert all enum values to their string representations
                audit_logs = [self._convert_enums_to_values(log) for log in audit_logs]
                self.db.audit_logs.insert_many(audit_logs)
                audit_logs = []
        
        # Insert remaining
        if audit_logs:
            # Convert all enum values to their string representations
            audit_logs = [self._convert_enums_to_values(log) for log in audit_logs]
            self.db.audit_logs.insert_many(audit_logs)
        
        logger.info(f"Inserted {count} audit logs")
    
    def generate_application_stats(self):
        """Generate application statistics by institution and funding program"""
        stats = []
        
        # Get all combinations of institutions, funding programs, and semesters
        institutions = list(self.db.institutions.find())
        funding_programs = list(self.db.funding_programs.find())
        semesters = ['2024.1', '2024.2', '2023.2', '2023.1']
        
        for institution in institutions:
            for program in funding_programs:
                for semester in semesters:
                    # Get applications for this combination
                    pipeline = [
                        {
                            '$match': {
                                'institution_id': institution['_id'],
                                'funding_program_id': program['_id'],
                                'semester': semester
                            }
                        },
                        {
                            '$group': {
                                '_id': '$status',
                                'count': {'$sum': 1},
                                'total_funding': {'$sum': '$approved_amount'}
                            }
                        }
                    ]
                    
                    results = list(self.db.applications.aggregate(pipeline))
                    
                    if not results:
                        continue
                    
                    # Calculate statistics
                    total_applications = sum(r['count'] for r in results)
                    approved_count = next((r['count'] for r in results if r['_id'] == ApplicationStatus.APPROVED), 0)
                    enrolled_count = next((r['count'] for r in results if r['_id'] == ApplicationStatus.ENROLLED), 0)
                    rejected_count = next((r['count'] for r in results if r['_id'] == ApplicationStatus.REJECTED), 0)
                    pending_count = total_applications - approved_count - enrolled_count - rejected_count
                    
                    total_approved = approved_count + enrolled_count
                    approval_rate = total_approved / total_applications if total_applications > 0 else 0
                    
                    total_funding = sum(r['total_funding'] or 0 for r in results if r['_id'] in [ApplicationStatus.APPROVED, ApplicationStatus.ENROLLED])
                    
                    # Get rejection reasons
                    rejection_pipeline = [
                        {
                            '$match': {
                                'institution_id': institution['_id'],
                                'funding_program_id': program['_id'],
                                'semester': semester,
                                'status': ApplicationStatus.REJECTED
                            }
                        },
                        {
                            '$group': {
                                '_id': '$rejection_reason',
                                'count': {'$sum': 1}
                            }
                        },
                        {
                            '$sort': {'count': -1}
                        },
                        {
                            '$limit': 5
                        }
                    ]
                    
                    top_rejection_reasons = [
                        {'reason': r['_id'], 'count': r['count']}
                        for r in self.db.applications.aggregate(rejection_pipeline)
                    ]
                    
                    # Calculate average processing time
                    time_pipeline = [
                        {
                            '$match': {
                                'institution_id': institution['_id'],
                                'funding_program_id': program['_id'],
                                'semester': semester,
                                'decision_date': {'$exists': True}
                            }
                        },
                        {
                            '$project': {
                                'processing_days': {
                                    '$divide': [
                                        {'$subtract': ['$decision_date', '$submission_date']},
                                        1000 * 60 * 60 * 24  # Convert to days
                                    ]
                                }
                            }
                        },
                        {
                            '$group': {
                                '_id': None,
                                'avg_days': {'$avg': '$processing_days'}
                            }
                        }
                    ]
                    
                    avg_processing = list(self.db.applications.aggregate(time_pipeline))
                    avg_processing_days = 30.0  # Default value
                    if avg_processing and avg_processing[0].get('avg_days') is not None:
                        avg_processing_days = avg_processing[0]['avg_days']
                    
                    stat = {
                        '_id': ObjectId(),
                        'institution_id': institution['_id'],
                        'funding_program_id': program['_id'],
                        'semester': semester,
                        'total_applications': total_applications,
                        'approved_count': approved_count + enrolled_count,
                        'rejected_count': rejected_count,
                        'pending_count': pending_count,
                        'approval_rate': round(approval_rate, 3),
                        'average_processing_days': round(avg_processing_days, 1),
                        'total_funding_approved': float(total_funding),
                        'top_rejection_reasons': top_rejection_reasons,
                        'calculated_at': datetime.utcnow()
                    }
                    
                    stats.append(stat)
        
        # Bulk insert
        if stats:
            # Convert all enum values to their string representations
            stats = [self._convert_enums_to_values(stat) for stat in stats]
            self.db.application_stats.insert_many(stats)
            logger.info(f"Generated {len(stats)} application statistics")
    
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        for collection_name, collection_schema in self.database_schema.collections.items():
            collection = self.db[collection_name]
            
            for index_def in collection_schema.indexes:
                try:
                    # Build index specification
                    index_spec = []
                    for field, direction in index_def.keys.items():
                        if direction == IndexDirection.TEXT:
                            index_spec.append((field, 'text'))
                        elif direction == IndexDirection.GEO2D:
                            index_spec.append((field, '2d'))
                        else:
                            index_spec.append((field, direction.value))
                    
                    # Create index
                    kwargs = {}
                    if index_def.unique:
                        kwargs['unique'] = True
                    if index_def.sparse:
                        kwargs['sparse'] = True
                    if index_def.ttl_seconds:
                        kwargs['expireAfterSeconds'] = index_def.ttl_seconds
                    
                    collection.create_index(index_spec, **kwargs)
                    logger.info(f"Created index on {collection_name}: {index_spec}")
                    
                except errors.OperationFailure as e:
                    if "already exists" in str(e):
                        logger.info(f"Index already exists on {collection_name}: {index_spec}")
                    else:
                        logger.error(f"Failed to create index on {collection_name}: {e}")
    
    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        for collection_name in self.database_schema.collections.keys():
            self.db[collection_name].delete_many({})
            logger.info(f"Cleared collection: {collection_name}")
    
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        logger.info("Validating seed data...")
        
        # Check collection counts
        for collection_name in self.database_schema.collections.keys():
            count = self.db[collection_name].count_documents({})
            logger.info(f"{collection_name}: {count} documents")
        
        # Check referential integrity
        
        # 1. Check applications reference valid users (through students)
        invalid_apps = self.db.applications.aggregate([
            {
                '$lookup': {
                    'from': 'students',
                    'localField': 'applicant_id',
                    'foreignField': '_id',
                    'as': 'student'
                }
            },
            {
                '$match': {
                    'student': {'$size': 0}
                }
            },
            {
                '$count': 'invalid_count'
            }
        ])
        
        invalid_count = list(invalid_apps)
        if invalid_count:
            raise ValueError(f"Found {invalid_count[0]['invalid_count']} applications with invalid student references")
        
        # 2. Check documents reference valid applications
        invalid_docs = self.db.documents.aggregate([
            {
                '$lookup': {
                    'from': 'applications',
                    'localField': 'application_id',
                    'foreignField': '_id',
                    'as': 'application'
                }
            },
            {
                '$match': {
                    'application': {'$size': 0}
                }
            },
            {
                '$count': 'invalid_count'
            }
        ])
        
        invalid_count = list(invalid_docs)
        if invalid_count:
            raise ValueError(f"Found {invalid_count[0]['invalid_count']} documents with invalid application references")
        
        # 3. Check average documents per application
        avg_docs = self.db.applications.aggregate([
            {
                '$lookup': {
                    'from': 'documents',
                    'localField': '_id',
                    'foreignField': 'application_id',
                    'as': 'docs'
                }
            },
            {
                '$group': {
                    '_id': None,
                    'avg_docs': {'$avg': {'$size': '$docs'}}
                }
            }
        ])
        
        result = list(avg_docs)
        if result:
            avg = result[0]['avg_docs']
            logger.info(f"Average documents per application: {avg:.1f}")
            if avg < 20 or avg > 24:
                logger.warning(f"Average documents per application ({avg:.1f}) is outside expected range (20-24)")
        
        # Use the built-in comprehensive validation
        pydantic_models = {
            'users': User,
            'students': Student,
            'applications': Application,
            'documents': Document,
            'protocols': Protocol,
            'funding_programs': FundingProgram,
            'institutions': Institution,
            'workflows': Workflow,
            'notifications': Notification,
            'audit_logs': AuditLog,
            'application_stats': ApplicationStats
        }
        
        validation_results = self.validate_schema_and_indexes(
            sample_size=10,
            pydantic_models=pydantic_models
        )
        
        if not validation_results['validation_summary']['overall_success']:
            logger.error("Schema and index validation failed!")
            for coll, result in validation_results['collections'].items():
                if not result['success']:
                    logger.error(f"Collection {coll}: {result.get('error', 'Unknown error')}")
                    if 'validation_errors' in result:
                        for err in result['validation_errors'][:5]:  # Show first 5 errors
                            logger.error(f"  - {err}")
        else:
            logger.info("All validations passed successfully!")


# Usage
if __name__ == "__main__":
    # Initialize schema
    schema = BrazilianEdtechSchema()
    
    # Initialize seeder
    seeder = BrazilianEdtechSeeder("mongodb://localhost:27017", schema)
    
    # Clear existing data (optional)
    logger.info("Clearing existing data...")
    seeder.clear_database()
    
    # Seed with sample data
    logger.info("Starting database seeding...")
    seeder.seed_all_collections()
    
    # Create indexes
    logger.info("Creating indexes...")
    seeder.create_indexes()
    
    # Validate the seeded data
    logger.info("Validating data...")
    seeder.validate_seed_data()
    
    logger.info("Database seeding completed successfully!")