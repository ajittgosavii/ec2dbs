import math

class EC2DatabaseSizingCalculator:
    # AWS instance types - AMD only when enabled
    INSTANCE_TYPES = [
        # AMD-based instances
        {"type": "m6a.large", "vCPU": 2, "RAM": 8, "max_ebs_bandwidth": 4750, "family": "general", "processor": "AMD"},
        {"type": "m6a.xlarge", "vCPU": 4, "RAM": 16, "max_ebs_bandwidth": 9500, "family": "general", "processor": "AMD"},
        {"type": "m6a.2xlarge", "vCPU": 8, "RAM": 32, "max_ebs_bandwidth": 19000, "family": "general", "processor": "AMD"},
        {"type": "m6a.4xlarge", "vCPU": 16, "RAM": 64, "max_ebs_bandwidth": 38000, "family": "general", "processor": "AMD"},
        {"type": "m6a.8xlarge", "vCPU": 32, "RAM": 128, "max_ebs_bandwidth": 47500, "family": "general", "processor": "AMD"},
        {"type": "r6a.large", "vCPU": 2, "RAM": 16, "max_ebs_bandwidth": 4750, "family": "memory", "processor": "AMD"},
        {"type": "r6a.xlarge", "vCPU": 4, "RAM": 32, "max_ebs_bandwidth": 9500, "family": "memory", "processor": "AMD"},
        {"type": "r6a.2xlarge", "vCPU": 8, "RAM": 64, "max_ebs_bandwidth": 19000, "family": "memory", "processor": "AMD"},
        {"type": "r6a.4xlarge", "vCPU": 16, "RAM": 128, "max_ebs_bandwidth": 38000, "family": "memory", "processor": "AMD"},
        {"type": "r6a.8xlarge", "vCPU": 32, "RAM": 256, "max_ebs_bandwidth": 47500, "family": "memory", "processor": "AMD"},
        {"type": "c6a.large", "vCPU": 2, "RAM": 4, "max_ebs_bandwidth": 4750, "family": "compute", "processor": "AMD"},
        {"type": "c6a.xlarge", "vCPU": 4, "RAM": 8, "max_ebs_bandwidth": 9500, "family": "compute", "processor": "AMD"},
        {"type": "c6a.2xlarge", "vCPU": 8, "RAM": 16, "max_ebs_bandwidth": 19000, "family": "compute", "processor": "AMD"},
        {"type": "c6a.4xlarge", "vCPU": 16, "RAM": 32, "max_ebs_bandwidth": 38000, "family": "compute", "processor": "AMD"},
        {"type": "c6a.8xlarge", "vCPU": 32, "RAM": 64, "max_ebs_bandwidth": 47500, "family": "compute", "processor": "AMD"},
        
        # Intel-based instances
        {"type": "m6i.large", "vCPU": 2, "RAM": 8, "max_ebs_bandwidth": 4750, "family": "general", "processor": "Intel"},
        {"type": "m6i.xlarge", "vCPU": 4, "RAM": 16, "max_ebs_bandwidth": 9500, "family": "general", "processor": "Intel"},
        {"type": "m6i.2xlarge", "vCPU": 8, "RAM": 32, "max_ebs_bandwidth": 19000, "family": "general", "processor": "Intel"},
        {"type": "m6i.4xlarge", "vCPU": 16, "RAM": 64, "max_ebs_bandwidth": 38000, "family": "general", "processor": "Intel"},
        {"type": "m6i.8xlarge", "vCPU": 32, "RAM": 128, "max_ebs_bandwidth": 47500, "family": "general", "processor": "Intel"},
        {"type": "r6i.large", "vCPU": 2, "RAM": 16, "max_ebs_bandwidth": 4750, "family": "memory", "processor": "Intel"},
        {"type": "r6i.xlarge", "vCPU": 4, "RAM": 32, "max_ebs_bandwidth": 9500, "family": "memory", "processor": "Intel"},
        {"type": "r6i.2xlarge", "vCPU": 8, "RAM": 64, "max_ebs_bandwidth": 19000, "family": "memory", "processor": "Intel"},
        {"type": "r6i.4xlarge", "vCPU": 16, "RAM": 128, "max_ebs_bandwidth": 38000, "family": "memory", "processor": "Intel"},
        {"type": "r6i.8xlarge", "vCPU": 32, "RAM": 256, "max_ebs_bandwidth": 47500, "family": "memory", "processor": "Intel"},
        {"type": "c6i.large", "vCPU": 2, "RAM": 4, "max_ebs_bandwidth": 4750, "family": "compute", "processor": "Intel"},
        {"type": "c6i.xlarge", "vCPU": 4, "RAM": 8, "max_ebs_bandwidth": 9500, "family": "compute", "processor": "Intel"},
        {"type": "c6i.2xlarge", "vCPU": 8, "RAM": 16, "max_ebs_bandwidth": 19000, "family": "compute", "processor": "Intel"},
        {"type": "c6i.4xlarge", "vCPU": 16, "RAM": 32, "max_ebs_bandwidth": 38000, "family": "compute", "processor": "Intel"},
        {"type": "c6i.8xlarge", "vCPU": 32, "RAM": 64, "max_ebs_bandwidth": 47500, "family": "compute", "processor": "Intel"},
    ]
    
    # Environment multipliers
    ENV_MULTIPLIERS = {
        "PROD": {"cpu_ram": 1.0, "storage": 1.0},
        "SQA": {"cpu_ram": 0.75, "storage": 0.7},
        "QA": {"cpu_ram": 0.6, "storage": 0.5},
        "DEV": {"cpu_ram": 0.4, "storage": 0.3}
    }
    
    def __init__(self):
        self.inputs = {
            "on_prem_cores": 16,
            "peak_cpu_percent": 65,
            "on_prem_ram_gb": 64,
            "peak_ram_percent": 75,
            "storage_current_gb": 500,
            "storage_growth_rate": 0.15,
            "peak_iops": 8000,
            "peak_throughput_mbps": 400,
            "years": 3,
            "workload_profile": "general",
            "prefer_amd": True
        }
    
    def calculate_requirements(self, env):
        """Calculate requirements for a specific environment"""
        mult = self.ENV_MULTIPLIERS[env]
        
        # Calculate compute requirements with min 2 vCPUs
        vcpus = self.inputs["on_prem_cores"] * (self.inputs["peak_cpu_percent"] / 100)
        vcpus = vcpus * (1 + 0.2) / 0.7 * mult["cpu_ram"]
        vcpus = max(math.ceil(vcpus), 2)  # Minimum 2 vCPUs
        
        ram = self.inputs["on_prem_ram_gb"] * (self.inputs["peak_ram_percent"] / 100)
        ram = ram * (1 + 0.2) / 0.7 * mult["cpu_ram"]
        ram = max(math.ceil(ram), 4)  # Minimum 4GB RAM
        
        # Calculate storage requirements with min 20GB
        growth_factor = (1 + self.inputs["storage_growth_rate"]) ** self.inputs["years"]
        storage = self.inputs["storage_current_gb"] * growth_factor
        storage = storage * (1 + 0.3) * mult["storage"]
        storage = max(math.ceil(storage), 20)  # Minimum 20GB
        
        # Calculate I/O requirements
        iops_required = self.inputs["peak_iops"] * (1 + 0.3)
        iops_required = math.ceil(iops_required)
        
        throughput_required = self.inputs["peak_throughput_mbps"] * (1 + 0.3)
        throughput_required = math.ceil(throughput_required)
        
        # Determine EBS type
        ebs_type = "io2" if (iops_required > 16000 or throughput_required > 1000) else "gp3"
        
        # Select instance
        instance = self.select_instance(
            vcpus, ram, throughput_required, 
            self.inputs["workload_profile"], 
            self.inputs["prefer_amd"]
        )
        
        return {
            "environment": env,
            "instance_type": instance["type"],
            "vCPUs": vcpus,
            "RAM_GB": ram,
            "storage_GB": storage,
            "ebs_type": ebs_type,
            "iops_required": iops_required,
            "throughput_required": f"{throughput_required} MB/s",
            "family": instance["family"],
            "processor": instance["processor"]
        }
    
    def select_instance(self, required_vcpus, required_ram, required_throughput, workload_profile, prefer_amd):
        """Select appropriate EC2 instance with AMD preference for cost savings"""
        candidates = []
        
        # Filter instances based on AMD preference
        filtered_instances = [
            i for i in self.INSTANCE_TYPES 
            if prefer_amd or i["processor"] != "AMD"
        ]
        
        for instance in filtered_instances:
            # Filter by workload profile
            if workload_profile != "general" and instance["family"] != workload_profile:
                continue
                
            # Check if meets minimum requirements
            if (instance["vCPU"] >= required_vcpus and 
                instance["RAM"] >= required_ram and
                instance["max_ebs_bandwidth"] >= (required_throughput * 1.2)):
                candidates.append(instance)
        
        # If no candidates found, return largest available
        if not candidates:
            return max(filtered_instances, key=lambda x: x["vCPU"])
        
        # Prioritize AMD for cost savings if enabled
        if prefer_amd:
            amd_candidates = [i for i in candidates if i["processor"] == "AMD"]
            if amd_candidates:
                # Return smallest AMD instance that meets requirements
                return min(amd_candidates, key=lambda x: x["vCPU"])
        
        # Return smallest Intel instance
        return min(candidates, key=lambda x: x["vCPU"])
    
    def generate_all_recommendations(self):
        """Generate recommendations for all environments"""
        results = {}
        for env in self.ENV_MULTIPLIERS.keys():
            results[env] = self.calculate_requirements(env)
        return results