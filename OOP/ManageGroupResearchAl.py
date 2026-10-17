from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel,Field,field_validator,ValidationError
class StudentInput(BaseModel):
     name:str=Field(min_length=1)
     year_of_birth:int=Field(ge=1950,le=2015)
     major:str=Field(min_length=1)
     @field_validator("name")
     @classmethod
     def validate_name(cls,value:str)->str:
        if not value.strip():
             raise ValueError("Tên không được rỗng sau khi sử dụng strip()")
        return value.strip()
class MentorInput(BaseModel):
     name:str=Field(min_length=1)
     year_of_birth:int=Field(ge=1950,le=2015)
     expertise:str=Field(min_length=1)
     @field_validator("name")
     @classmethod
     def validate_name(cls,value:str)->str:
        if not value.strip():
             raise ValueError("Tên không được rỗng sau khi sử dụng strip()")
        return value.strip()
class EngineerInput(BaseModel):
     name:str=Field(min_length=1)
     year_of_birth:int=Field(ge=1950,le=2015)
     tech_stack:str=Field(min_length=1)
     @field_validator("name")
     @classmethod
     def validate_name(cls,value:str)->str:
        if not value.strip():
             raise ValueError("Tên không được rỗng sau khi sử dụng strip()")
        return value.strip()
class Member(ABC):
    def __init__(self,name:str, year_of_birth:int):
        self.name=name
        self.year_of_birth=year_of_birth

    @property
    def name(self)->str:
          return self._name
    @name.setter
    def name(self,newname:str)->None:
          if not isinstance(newname,str) or not newname.strip():
                raise ValueError("Tên không được rỗng sau khi sử dụng")
          self._name=newname.strip()

    @property
    def year_of_birth(self)->int:
          return self._year_of_birth
    @year_of_birth.setter
    def year_of_birth(self,yob:int)->None:
        if not isinstance(yob,int) or isinstance(yob,bool):
            raise ValueError("Năm sinh bắt buộc phải là số nguyên")
        if not (1950<=yob<=2015):
            raise ValueError("Năm sinh bắt buộc nằm trong khoảng [1950,2015]")
        self._year_of_birth=yob
    @staticmethod
    def valid_birth_year(vby)->bool:
        return(
            isinstance(vby,int)
            and not isinstance(vby,bool)
            and 1950<=vby<= 2015
        )
    
    @abstractmethod
    def role(self)->str:
       pass
    @abstractmethod
    def describe(self)->str:
        pass

class StudentMember(Member):
    def __init__(self,name:str, year_of_birth:int, major:str):
        super().__init__(name,year_of_birth)
        self.major=major

    def role(self)->str:
        return "StudentMember"
    def describe(self)->str:
        return(
            f"The disciption of {self.name}:"
            f"Year of birth: {self.year_of_birth}"
            f"Position: {self.role()}"
            f"Major: {self.major}"
        )
    @classmethod
    def from_dict(cls,data:dict)->"StudentMember":
         validate_data=StudentInput.model_validate(data)
         return cls(**validate_data.model_dump())


class Mentor(Member):
    def __init__(self,name:str, year_of_birth:int, expertise:str):
            super().__init__(name,year_of_birth)
            self.expertise=expertise

    def role(self)->str:
        return "Mentor"
    def describe(self)->str:
            return(f"The disciption of {self.name}:" 
                    f"Year of birth: {self.year_of_birth}"
                   f"Position: {self.role()}"
                    f"Expertise: {self.expertise}")
    @classmethod
    def from_dict(cls,data:dict)->"Mentor":
         validate_data=MentorInput.model_validate(data)
         return cls(**validate_data.model_dump())
class Engineer(Member):
    def __init__(self,name:str, year_of_birth:int, tech_stack:str):
                super().__init__(name,year_of_birth)
                self.tech_stack=tech_stack

    def role(self)->str:
        return "Engineer"
    def describe(self)->str:
                return(f"The disciption of {self.name}:" 
                        f"Year of birth: {self.year_of_birth}"
                       f"Position: {self.role()}"
                        f"Domain engineer: {self.tech_stack}")
    @classmethod
    def from_dict(cls,data:dict)->"Engineer":
         validate_data=EngineerInput.model_validate(data)
         return cls(**validate_data.model_dump())# ** có tác dụng giải nén dictionary thành các đối số có key và values .
@dataclass(frozen=True) #immutable
class LabReport:
     lab_name:str
     total_members:int
     student_count:int
     mentor_count:int
     engineer_count:int

class LabGroup:
    organization="DUT AI"
    def __init__(self,name:str):
          self.name=name
          self.members:list[Member]=[]
    def add_member(self,member:Member)->None:
        if not isinstance(member,Member):
             raise TypeError("Đối tượng thành viên này phải thuộc lớp Member")
        self.members.append(member)
    def describe(self)->str:
        description=[member.describe() for member in self.members]
        return "\n".join(description)
    def count_by_role(self,role:str)->int:
         count=0
         for member in self.members:
              if member.role()==role:
                   count+=1
         return count
    def sort_by_age(self)->None:
         self.members.sort(key=lambda member:member.year_of_birth,reverse=True)
    def average_birth_year_of_mentors(self)->float|None:
         mentors=[member for member in self.members if isinstance(member,Mentor)]
         if not mentors:return None
         total_birth_year=sum(mentor.year_of_birth for mentor in mentors)
         return total_birth_year/len(mentors)
    def to_report(self)->LabReport:
         return LabReport(
              lab_name=self.name,
              total_members=len(self.members),
              student_count=self.count_by_role("StudentMember"),
              mentor_count=self.count_by_role("Mentor"),
              engineer_count=self.count_by_role("Engineer"),
        )
    @classmethod
    def from_members(cls,name:str,members:list[Member])->"LabGroup":
         group=cls(name)
         for member in members:
            group.add_member(member)
         return group
    '''from_members có tác dụng thay vì tạo nhóm rồi gọi add_member() nhiều lần, 
    ta có thể tạo nhóm trực tiếp từ một list[]'''

if __name__ == "__main__":
    print("=== BẮT ĐẦU KIỂM THỬ CHƯƠNG TRÌNH ===\n")

    # 1. Tạo nhóm NLP Lab
    members_list = [
        StudentMember("An", 2005, "Data Science"),
        Mentor("Bình", 1990, "NLP"),
        Mentor("Chi", 1988, "Computer Vision"),
        Engineer("Dũng", 1999, "Python"),
    ]
    lab = LabGroup.from_members("NLP Lab", members_list)

    # 2. Kiểm tra số lượng Mentor
    assert lab.count_by_role("Mentor") == 2
    print("[PASS] count_by_role('Mentor') = 2")

    # 3. Kiểm tra năm sinh trung bình của Mentor
    assert lab.average_birth_year_of_mentors() == 1989.0
    print("[PASS] average_birth_year_of_mentors() = 1989.0")

    # 4. Kiểm tra báo cáo
    report = lab.to_report()
    assert report.total_members == 4
    print(f"[PASS] to_report().total_members = {report.total_members}")

    # 5. Kiểm tra sắp xếp tuổi
    lab.sort_by_age()
    sorted_years = [m.year_of_birth for m in lab.members]
    assert sorted_years == [2005, 1999, 1990, 1988]
    print(f"[PASS] sort_by_age() = {sorted_years}")

    # 6. Kiểm tra describe() và biến lớp
    assert LabGroup.organization == "DUT AI"
    assert lab.organization == "DUT AI"
    print(f"[PASS] organization = {lab.organization}")
    print("\n--- lab.describe() ---")
    print(lab.describe())

    # 7a. Kiểm tra ValueError khi khởi tạo trực tiếp
    try:
        StudentMember("Nam", 2022, "AI")
        assert False, "Không phát sinh ValueError"
    except ValueError:
        print("\n[PASS] Năm sinh 2022 phát sinh ValueError")

    # 7b. Kiểm tra ValidationError từ Pydantic
    try:
        Mentor.from_dict({
            "name": "Nam",
            "year_of_birth": 2022,
            "expertise": "AI"
        })
        assert False, "Không phát sinh ValidationError"
    except ValidationError:
        print("[PASS] Năm sinh 2022 phát sinh ValidationError")

    # 8. Kiểm tra TypeError khi thêm thành viên sai kiểu
    try:
        lab.add_member("An")
        assert False, "Không phát sinh TypeError"
    except TypeError:
        print("[PASS] add_member('An') phát sinh TypeError")

    print("\n=== TẤT CẢ CÁC BÀI KIỂM THỬ ĐỀU THÀNH CÔNG! ===")


     
         
