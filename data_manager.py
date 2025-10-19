import json
import os
from typing import List, Dict, Optional

class DataManager:
    """Manages data persistence for the mosque member management system"""
    
    def __init__(self, data_file: str = "members_data.json"):
        self.data_file = data_file
        self.members = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """Load member data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            return []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading data: {e}")
            return []
    
    def _save_data(self) -> bool:
        """Save member data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.members, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def add_member(self, member_data: Dict) -> bool:
        """Add a new member"""
        try:
            # Ensure points field exists
            if 'points' not in member_data:
                member_data['points'] = 0
            
            self.members.append(member_data)
            return self._save_data()
        except Exception as e:
            print(f"Error adding member: {e}")
            return False
    
    def get_all_members(self) -> List[Dict]:
        """Get all members"""
        # Reload data to ensure we have the latest version
        self.members = self._load_data()
        return self.members.copy()
    
    def get_member(self, index: int) -> Optional[Dict]:
        """Get a specific member by index"""
        try:
            self.members = self._load_data()
            if 0 <= index < len(self.members):
                return self.members[index].copy()
            return None
        except Exception as e:
            print(f"Error getting member: {e}")
            return None
    
    def update_member(self, index: int, updated_data: Dict) -> bool:
        """Update a member's information"""
        try:
            self.members = self._load_data()
            if 0 <= index < len(self.members):
                # Preserve points if not in updated data
                if 'points' not in updated_data:
                    updated_data['points'] = self.members[index].get('points', 0)
                
                self.members[index] = updated_data
                return self._save_data()
            return False
        except Exception as e:
            print(f"Error updating member: {e}")
            return False
    
    def update_member_points(self, index: int, new_points: int, reason: str = "") -> bool:
        """Update a member's points and log the change"""
        try:
            self.members = self._load_data()
            if 0 <= index < len(self.members):
                old_points = self.members[index].get('points', 0)
                self.members[index]['points'] = max(0, new_points)  # Ensure points don't go negative
                
                # Initialize history if it doesn't exist
                if 'points_history' not in self.members[index]:
                    self.members[index]['points_history'] = []
                
                # Add history entry
                from datetime import datetime
                change = new_points - old_points
                history_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'old_points': old_points,
                    'new_points': new_points,
                    'change': change,
                    'reason': reason
                }
                self.members[index]['points_history'].append(history_entry)
                
                return self._save_data()
            return False
        except Exception as e:
            print(f"Error updating member points: {e}")
            return False
    
    def get_member_history(self, index: int) -> list:
        """Get points history for a specific member"""
        try:
            self.members = self._load_data()
            if 0 <= index < len(self.members):
                return self.members[index].get('points_history', [])
            return []
        except Exception as e:
            print(f"Error getting member history: {e}")
            return []
    
    def delete_member(self, index: int) -> bool:
        """Delete a member"""
        try:
            self.members = self._load_data()
            if 0 <= index < len(self.members):
                del self.members[index]
                return self._save_data()
            return False
        except Exception as e:
            print(f"Error deleting member: {e}")
            return False
    
    def get_leaderboard(self) -> List[Dict]:
        """Get members sorted by points (highest first)"""
        self.members = self._load_data()
        return sorted(self.members, key=lambda x: x.get('points', 0), reverse=True)
    
    def get_member_count(self) -> int:
        """Get total number of members"""
        self.members = self._load_data()
        return len(self.members)
    
    def backup_data(self, backup_file: str = None) -> bool:
        """Create a backup of the current data"""
        try:
            if backup_file is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"members_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.members, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """Restore data from a backup file"""
        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.members = data
                        return self._save_data()
            return False
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """Clear all member data (use with caution)"""
        try:
            self.members = []
            return self._save_data()
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def export_to_csv(self, csv_file: str = "members_export.csv") -> bool:
        """Export member data to CSV format"""
        try:
            import pandas as pd
            
            if not self.members:
                return False
            
            df = pd.DataFrame(self.members)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
