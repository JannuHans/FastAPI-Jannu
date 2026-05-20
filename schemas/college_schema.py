from pydantic import BaseModel, ConfigDict, EmailStr


class StudentSchema(BaseModel):
    name: str
    email: EmailStr
    age: int


class StudentResponse(StudentSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CourseSchema(BaseModel):
    name: str
    description: str
    duration: str


class CourseResponse(CourseSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EnrollmentSchema(BaseModel):
    student_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    student_id: int
    course_ids: list[int]


class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
