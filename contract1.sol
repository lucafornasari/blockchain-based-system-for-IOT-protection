pragma solidity ^0.7.4;
// SPDX-License-Identifier: AFL-1.1

contract testContract {
    
    address[] nodes;                                            // Contains the list of nodes connected
    mapping (address => nodeInformation) nodesInformation;      // Map that for each node address stores the position and ip
    mapping (string => address) nodesIPs;                       // Map that for each ip refers the address, needed because in Solidity we can't loop over a map
    string[] ips;                                               // Contains the list of ips, needed for the same reason of the previous map
    uint nCounter = 0;                                          // ?? Counter that contains the number of nodes connected (maybe not needed, to check later) ??
    
    struct nodeInformation{
        
        uint position;
        string ip;
        
    }
    
    
    struct trustResult{
        
        address trustor;
        address trustee;
        uint trust;
        
    }
    

    
    mapping (address => string[]) pruningResult;                // Map that for each node stores the pruning result, it's used by nodes to read the array of IPs. It's better to not include that information inside the event for gas fees reason
    mapping (uint => trustResult) trusts;                     // Map that contains the results of trusts calculated
    uint trCounter = 0;
    
    event ProbingStarted(address indexed trustor);
    
    
    
    /* * * * * * * * * * * * * * * * * * * * * * * * * * 
     *          Functions that edit the maps           *
     * * * * * * * * * * * * * * * * * * * * * * * * * */
     
     // Function called from a node when it connects to the blockchain
     function connect(uint position, string calldata ip) public{
        
        nodes.push(msg.sender);
        nodesInformation[msg.sender].position = position;
        nodesInformation[msg.sender].ip = ip;
        nodesIPs[ip] = msg.sender;
        ips.push(ip);
        nCounter++;
        
     }
     
     // Function called from a node to advise the contract that it is starting a probing transaction
     function probingTransaction(string calldata _trustee) public{
        
        bool exists = false;
        for(uint i=0; i<nCounter; i++){
            if(keccak256(abi.encodePacked(_trustee)) == keccak256(abi.encodePacked(ips[i]))){   // Comparing two stirngs, it's the only way to do it
                exists = true;
            }
        }
        
        if(exists){
            
           address trustee = nodesIPs[_trustee];
           string[] storage prunedNodes;
           
           for(uint i=0; i<nCounter; i++){
                if(abs(nodesInformation[nodes[i]].position - nodesInformation[trustee].position) < 10){
                    prunedNodes.push(nodesInformation[nodes[i]].ip);
                }
           }
           
           pruningResult[msg.sender] = prunedNodes;
           
           emit ProbingStarted(msg.sender);     //emits an event
        }
     }
     
     // Function called from a node when, catched the event emitted from the contract, wants to calculate the trust
     function calculateTrust(uint tdata, uint[] calldata datas, string calldata _trustee) public{
         
         uint avrg = avg(datas);
         uint max;
         
         if(avrg > tdata){
             max = avrg;
         } else {
             max = tdata;
         }
         
         uint trust = abs(tdata - avrg) / max;
         
         trustResult memory result;
         result.trustor = msg.sender;
         result.trustee = nodesIPs[_trustee];
         result.trust = trust;
         
         trusts[nCounter] = result;
         nCounter++;

     }
     
     

    /* * * * * * * * * * * * * * * * * * * * * * * * * * 
     * Getter Functions, marked by the key word "view" *
     * * * * * * * * * * * * * * * * * * * * * * * * * */
     
     // Function called from a node when wants to read a pruning result, unfortunately Solidity doesn't support the return of a dynamic array, so it must be read more times
     function getPruningResult(uint i) public returns (string memory, bool){
         
        if(i == pruningResult[msg.sender].length - 1){
            string memory buff = pruningResult[msg.sender][i];
            clearPruningArray(msg.sender);
            return (buff, false);
        } else {
            return (pruningResult[msg.sender][i], true);
        }
        
     }
     
     
     
    /* * * * * * * * * * * * * * * * * * * * * * * * * * * 
     * Private Functions, needed for internal operations *
     * * * * * * * * * * * * * * * * * * * * * * * * * * */   
    
    // In Solidity it doesn't exists a function for absolute value
    function abs(uint x) private pure returns (uint) {
        return x >= 0 ? x : -x;
    }
    
    function clearPruningArray(address a) private {
        delete pruningResult[a];
    }
    
    function avg(uint[] calldata d) private pure returns (uint) {
        uint sum = 0;
        for (uint i = 0; i < d.length; i++) {
            sum += d[i];
        }
        return sum/d.length;
    }
    
}