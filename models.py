# models.py
from sqlmodel import SQLModel, Field, Relationship, Session
from typing import Optional, List, ForwardRef
from datetime import datetime
from sqlalchemy import Column, CheckConstraint


# Base Models
class BaseModel(SQLModel):
    """
    A base class for shared functionality across all models.
    """
    created_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_edited_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column=Column(onupdate=datetime.utcnow))

    def __repr__(self):
        """
        Return a string representation of the object.
        """
        field_values = ", ".join(
            f"{key}={value}" for key, value in vars(self).items() if not key.startswith("_")
        )
        return f"<{self.__class__.__name__}({field_values})>"

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}

    @classmethod
    def from_dict(cls, data):
        """
        Create an instance from a dictionary.
        """
        return cls(**data)


# User Model
class User(BaseModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    workout_sessions: List["WorkoutSession"] = Relationship(back_populates="user")


# Workout Type and Exercise Models
class WorkoutType(BaseModel, table=True):
    workout_type_id: Optional[int] = Field(default=None, primary_key=True)
    workout_name: str
    muscle_group_targeted: str
    category_type: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    exercises: List["Exercise"] = Relationship(back_populates="workout_type")


class Exercise(BaseModel, table=True):
    exercise_id: Optional[int] = Field(default=None, primary_key=True)
    workout_type_id: Optional[int] = Field(foreign_key="workouttype.workout_type_id")
    exercise_name: str
    description: Optional[str] = None
    equipment_required: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    difficulty_level: Optional[str] = None
    calories_burned_per_minute: Optional[float] = None
    muscle_groups_secondary: Optional[str] = None
    video_tutorial_link: Optional[str] = None
    image_url: Optional[str] = None
    workout_type: Optional[WorkoutType] = Relationship(back_populates="exercises")
    exercise_logs: List["ExerciseLog"] = Relationship(back_populates="exercise")


# Workout Session Model
class WorkoutSession(BaseModel, table=True):
    session_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    workout_date: datetime = Field(default_factory=datetime.utcnow)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: Optional[int] = None
    location: Optional[str] = None
    perceived_exertion: Optional[int] = None
    notes: Optional[str] = None
    workout_source: Optional[str] = None
    user: Optional[User] = Relationship(back_populates="workout_sessions")
    exercise_logs: List["ExerciseLog"] = Relationship(back_populates="session")


# Exercise Log Model
class ExerciseLog(BaseModel, table=True):
    exercise_log_id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workoutsession.session_id")
    exercise_id: int = Field(foreign_key="exercise.exercise_id")
    set_number: Optional[int] = None
    repetitions: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[int] = None
    rest_time: Optional[int] = None
    notes: Optional[str] = None
    difficulty_level: Optional[str] = None
    session: Optional[WorkoutSession] = Relationship(back_populates="exercise_logs")
    exercise: Optional[Exercise] = Relationship(back_populates="exercise_logs")


# Resolve forward references
User.update_forward_refs()
WorkoutType.update_forward_refs()
Exercise.update_forward_refs()
WorkoutSession.update_forward_refs()
ExerciseLog.update_forward_refs()


# Example function to query the WorkoutType table
def query_workout_type_table(engine):
    """
    Example: Querying the WorkoutType table
    """
    with Session(engine) as session:
        new_workout = WorkoutType(
            workout_name="Strength Training",
            muscle_group_targeted="Full Body",
            category_type="Weightlifting",
            description="A high-intensity workout for muscle building.",
        )
        session.add(new_workout)
        session.commit()


# Example function to create a workout session with exercise logs
def create_workout_session(engine, user_id):
    """
    Example: Creating a workout session with exercise logs
    """
    with Session(engine) as session:
        # Find some exercises
        exercises = session.query(Exercise).limit(3).all()
        
        if not exercises:
            print("No exercises found. Please add exercises first.")
            return
        
        # Create a new workout session
        workout_session = WorkoutSession(
            user_id=user_id,
            workout_date=datetime.utcnow(),
            start_time=datetime.utcnow(),
            location="Home Gym",
            perceived_exertion=7,
            notes="Felt strong today",
        )
        session.add(workout_session)
        session.flush()  # Flush to get the session_id
        
        # Add exercise logs for this session
        for i, exercise in enumerate(exercises, 1):
            for set_num in range(1, 4):  # 3 sets for each exercise
                exercise_log = ExerciseLog(
                    session_id=workout_session.session_id,
                    exercise_id=exercise.exercise_id,
                    set_number=set_num,
                    repetitions=10 if set_num < 3 else 8,  # Decrease reps in last set
                    weight=50.0 if exercise.primary_muscle_group in ["Chest", "Back", "Legs"] else 25.0,
                    rest_time=60,  # 60 seconds rest
                    difficulty_level="Medium",
                )
                session.add(exercise_log)
        
        # Set end time after all exercises are done
        workout_session.end_time = datetime.utcnow()
        # Calculate duration in minutes
        delta = workout_session.end_time - workout_session.start_time
        workout_session.total_duration = int(delta.total_seconds() / 60)
        
        session.commit()