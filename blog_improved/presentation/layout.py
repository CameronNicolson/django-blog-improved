from dataclasses import dataclass, field

@dataclass
class Spacing:
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    def horizontal(self) -> int:
        """Returns the total horizontal spacing (left + right)."""
        return self.left + self.right

    def vertical(self) -> int:
        """Returns the total vertical spacing (top + bottom)."""
        return self.top + self.bottom

    def __str__(self) -> str:
        """String representation of the spacing values."""
        return f"Spacing(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom})"

@dataclass
class Border:
    thickness: int = 0 
    style: str = None

@dataclass
class Layout:
    wdith: int = 0
    height: int = 0
    padding: Spacing = field(default_factory=Spacing) 
    margin: Spacing = field(default_factory=Spacing) 
    border: Spacing = field(default_factory=Border) 

