import hashlib
import json
import time
from typing import List

class Block:
    def __init__(self, index: int, votes: List[dict], timestamp: float, previous_hash: str, nonce=0):
        self.index = index
        self.votes = votes
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'votes': self.votes,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        # Proof-of-work: hash must start with '0' * difficulty
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_votes: List[dict] = []
        self.voters = set()  # Track voter IDs that have voted

    def create_genesis_block(self):
        return Block(0, [], time.time(), '0')

    def get_latest_block(self):
        return self.chain[-1]

    def add_vote(self, voter_id: str, candidate: str):
        voter_hash = hashlib.sha256(voter_id.encode()).hexdigest()
        if voter_hash in self.voters:
            print("Voter with this ID has already voted!")
            return False
        vote = {
            'voter_hash': voter_hash, 
            'candidate': candidate,
            'timestamp': time.time()
        }
        self.pending_votes.append(vote)
        self.voters.add(voter_hash)
        print(f"Vote accepted for candidate '{candidate}'")
        return True

    def mine_pending_votes(self):
        if not self.pending_votes:
            print("No votes to mine.")
            return False
        new_block = Block(
            index=len(self.chain),
            votes=self.pending_votes,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )
        print("Mining block...")
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_votes = []
        print("Block mined and added to blockchain.\n")
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            if current.hash != current.calculate_hash():
                print(f"Block {i} hash invalid!")
                return False

            if current.previous_hash != previous.hash:
                print(f"Block {i} previous hash does not match!")
                return False
        return True

    def tally_votes(self):
        results = {}
        for block in self.chain:
            for vote in block.votes:
                candidate = vote['candidate']
                results[candidate] = results.get(candidate, 0) + 1
        # Include pending votes too
        for vote in self.pending_votes:
            candidate = vote['candidate']
            results[candidate] = results.get(candidate, 0) + 1
        return results

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index} [Hash: {block.hash[:20]}...]")
            print(f"Previous Hash: {block.previous_hash[:20]}...")
            print(f"Nonce: {block.nonce}")
            print(f"Votes:")
            for vote in block.votes:
                print(f"  - Candidate: {vote['candidate']}, VoterHash: {vote['voter_hash'][:10]}..., Time: {time.ctime(vote['timestamp'])}")
            print("-" * 30)

def main():
    blockchain = Blockchain()

    while True:
        print("\n=== Blockchain Voting System ===")
        print("1. Cast Vote")
        print("2. Mine Pending Votes")
        print("3. Show Voting Results")
        print("4. Validate Blockchain Integrity")
        print("5. Show Blockchain Details")
        print("6. Exit")

        choice = input("Select an option (1-6): ").strip()

        if choice == '1':
            voter_id = input("Enter your Voter ID (unique): ").strip()
            candidate = input("Enter Candidate Name: ").strip()
            blockchain.add_vote(voter_id, candidate)

        elif choice == '2':
            blockchain.mine_pending_votes()

        elif choice == '3':
            results = blockchain.tally_votes()
            print("\n--- Voting Tally ---")
            for candidate, count in results.items():
                print(f"{candidate}: {count} vote(s)")

        elif choice == '4':
            if blockchain.is_chain_valid():
                print("Blockchain is valid and intact.")
            else:
                print("Blockchain integrity compromised!")

        elif choice == '5':
            blockchain.print_chain()

        elif choice == '6':
            print("Exiting voting system.")
            break

        else:
            print("Invalid option. Please select between 1-6.")

if __name__ == "__main__":
    main()
