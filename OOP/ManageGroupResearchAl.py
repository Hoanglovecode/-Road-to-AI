from abc import ABC, abstractmethod
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
class LabGroup:
    def __init__(self,name:str):
          self.name=name
          self.members:list[Member]=[]
    def add_member(self,member:Member)->None:
        if not isinstance(member,Member):
             raise TypeError("Đối tượng thành viên này phải thuộc lớp Member")
        self.members.append(member)
    def desribe(self)->str:
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
