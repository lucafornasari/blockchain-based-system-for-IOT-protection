pragma solidity ^0.7.4;
// SPDX-License-Identifier: AFL-1.1

contract testContract {
    
    address[] nodes;                                            // Array of connected nodes' addresses
    mapping (string => nodeInformation) nodesInformations;      // Map that for each node address stores the position and ip
    mapping (uint => trustResult) trusts;                       // Map that contains the results of trusts calculated
    mapping (address => string) nodesIps;
    uint nCounter = 0;
    uint probingThreshold = 20;
    
   
    // Struct that will contain all the informations about a connected node
    struct nodeInformation{
        
        uint position;
        string service;
        
    }
    
    // Struct that will contain a trust calculation result
    struct trustResult{
        
        string trustor_ip;
        string trustee_ip;
        uint trust;
        
    }
    
    mapping (string => uint) reputations;                       // Map that stores reputations of nodes
    
    /* * * * * * * * * * * * * * * * * * * * * * * * * * 
     *          Functions that edit the maps           *
     * * * * * * * * * * * * * * * * * * * * * * * * * */
     
    
     // Function called from a node when it connects to the blockchain
     function connect(uint position, string calldata service, string calldata ip) public{
        
        bool flag = true;
        
        for(uint i = 0; i < nodes.length; i++){
            
            if(nodes[i] == msg.sender){
                flag = false;
                break;
            }
            
        }
        
        if(flag && (nodesInformations[ip].position != 0) && (keccak256(abi.encodePacked(nodesIps[msg.sender])) != keccak256(abi.encodePacked("")))){    // Checks that node is not already connected and the IP is not already in
            
            nodes.push(msg.sender);
            nodesInformations[ip].position = position;
            nodesInformations[ip].service = service;
            nodesIps[msg.sender] = ip;
            
        }
        
     }
     
     
     
     // Function that edits informations of a specific node
     function changeInformations(uint position, string calldata service, string calldata ip) public{
         
         if(keccak256(abi.encodePacked(nodesIps[msg.sender])) == keccak256(abi.encodePacked(ip))){
             
            nodesInformations[ip].position = position;
            nodesInformations[ip].service = service;
            
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
         
         uint trust = (absSubtraction(tdata, avrg) * 100) / max;

         
         trustResult memory result;
         result.trustor_ip = nodesIps[msg.sender];
         result.trustee_ip = _trustee;
         result.trust = trust;
         
         trusts[nCounter] = result;
         nCounter++;
         
         if(nCounter == probingThreshold){
            calculateReputations();
            resetTrusts();
         }

     }
     
     
    /* * * * * * * * * * * * * * * * * * * * * * * * * * 
     * Getter Functions, marked by the key word "view" *
     * * * * * * * * * * * * * * * * * * * * * * * * * */
     
     
     // Getter function for the position of a specified node that is identified with ip
     function getPosition(string calldata ip) public view returns(uint){
         
         return nodesInformations[ip].position;
         
     }
     
     // Getter function for the service of a specified node that is identified with ip
     function getService(string calldata ip) public view returns(string memory){
         
         return nodesInformations[ip].service;
         
     }
     
     // Temporary, to delete
     function getTrust(uint _id) public view returns(uint){
         return trusts[_id].trust;
     }
     
     
     
    /* * * * * * * * * * * * * * * * * * * * * * * * * * * 
     * Private Functions, needed for internal operations *
     * * * * * * * * * * * * * * * * * * * * * * * * * * */   
    

    function absSubtraction(uint x1, uint x2) private pure returns (uint) {
        if(x1 > x2){
            return (x1 - x2);
        } else {
            return (x2 - x1);
        }
    }
    
    
    function avg(uint[] calldata d) private pure returns (uint) {
        uint sum = 0;
        for (uint i = 0; i < d.length; i++) {
            sum += d[i];
        }
        return sum/d.length;
    }
    
    
    function resetTrusts() private {
        
        for(uint i = 0; i < nCounter+1; i++){
            trusts[i].trustor_ip = "";
            trusts[i].trustee_ip = "";
            trusts[i].trust = 0;
        }
        
        nCounter = 0;
        
    }
    
    
    function calculateReputations() private {
        
        uint trCount = 0;
        uint trustSum = 0;
        
        for(uint i = 0; i< nodes.length; i++){
            
            string memory te = nodesIps[nodes[i]];
            
            for(uint j = 0; j< nCounter+1; j++){
                
                if(keccak256(abi.encodePacked(trusts[j].trustee_ip)) == keccak256(abi.encodePacked(te))){
                    
                    trustSum += trusts[j].trust;
                    trCount++;
                    
                }
                
            }
            
            uint reputation = trustSum / trCount;
            
            reputations[te] = (reputations[te] / 4) + reputation;
            
            trCount = 0;
            trustSum = 0;
            
        }
        
        
        
    }
    
    
    
}